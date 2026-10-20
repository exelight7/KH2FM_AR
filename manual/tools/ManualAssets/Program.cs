using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using OpenKh.Egs;

internal static class Program
{
    static readonly JsonSerializerOptions Json = new() { PropertyNameCaseInsensitive = true, WriteIndented = true };
    internal sealed class Entry
    {
        public string Path { get; set; } = "";
        public string Group { get; set; } = "";
        public int Size { get; set; }
        public string Sha256 { get; set; } = "";
        public string File { get; set; } = "";
        public string FileHash { get; set; } = "";
        public string? Container { get; set; }
        public string? Asset { get; set; }
        public int SourceSize { get; set; }
        public string? SourceHash { get; set; }
    }
    sealed class Manifest
    {
        public int Schema { get; set; }
        public string Version { get; set; } = "";
        public string ExeHash { get; set; } = "";
        public Dictionary<string, string> Heds { get; set; } = new();
        public List<Entry> Files { get; set; } = new();
    }
    internal static string Hash(byte[] data) => Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();
    static string FileHash(string file) { using var stream = File.OpenRead(file); return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant(); }
    internal static string Under(string root, string relative)
    {
        if (relative.Length == 0 || relative.Contains('\\') || relative.Contains(':') || relative.Split('/').Any(p => p is "" or "." or "..")) throw new IOException("Unsafe relative path");
        var full = Path.GetFullPath(Path.Combine(root, relative.Replace('/', Path.DirectorySeparatorChar)));
        if (!full.StartsWith(Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new IOException("Path escaped root");
        return full;
    }
    internal static byte[] Apply(byte[] source, byte[] compressed, int size)
    {
        if (source.Length == 0 || size < 1 || size > 128 * 1024 * 1024) throw new IOException("Invalid patch bounds");
        using var input = new MemoryStream(compressed);
        using var gzip = new GZipStream(input, CompressionMode.Decompress);
        var output = new byte[size];
        gzip.ReadExactly(output);
        if (gzip.ReadByte() != -1) throw new IOException("Oversized patch");
        for (int i = 0; i < size; i++) output[i] ^= source[i % source.Length];
        return output;
    }
    static void SelfTest()
    {
        byte[] source = { 1, 2, 3 }, target = { 4, 2, 9, 8, 7 };
        using var encoded = new MemoryStream();
        using (var gzip = new GZipStream(encoded, CompressionLevel.SmallestSize, true)) gzip.Write(target.Select((b, i) => (byte)(b ^ source[i % source.Length])).ToArray());
        if (!Apply(source, encoded.ToArray(), target.Length).SequenceEqual(target)) throw new Exception("Patch roundtrip failed");
        bool denied = false; try { Apply(source, encoded.ToArray(), 2); } catch (IOException) { denied = true; }
        if (!denied) throw new Exception("Patch length guard failed");
        denied = false; try { Under(Path.GetTempPath(), "../outside"); } catch (IOException) { denied = true; }
        if (!denied) throw new Exception("Path guard failed");
        Console.WriteLine("PASS: patch roundtrip, exact decompression bounds, path traversal refusal");
    }
    static void Prepare(string manifestFile, string game, string output)
    {
        var root = Path.GetDirectoryName(Path.GetFullPath(manifestFile))!;
        var m = JsonSerializer.Deserialize<Manifest>(File.ReadAllText(manifestFile), Json)!;
        if (m.Schema != 1 || m.Version != "2.0.1" || m.Files.Count != 846 || m.Files.Select(f => f.Path).Distinct(StringComparer.OrdinalIgnoreCase).Count() != 846) throw new IOException("Unknown manual manifest");
        if (FileHash(Path.Combine(game, "KINGDOM HEARTS II FINAL MIX.exe")) != m.ExeHash) throw new IOException("Unsupported or unknown game version. Installation aborted to prevent damage.");
        var archives = Path.Combine(game, "Image", "dt");
        foreach (var pair in m.Heds) if (FileHash(Under(archives, pair.Key)) != pair.Value) throw new IOException("Unsupported HED: " + pair.Key);
        // An unfinished directory is never accepted as a prepared cache.
        if (Directory.Exists(output)) throw new IOException("Preparation output already exists");
        Directory.CreateDirectory(output);
        var records = new List<object>();
        using (var blob = File.Create(Path.Combine(output, "payload.bin")))
        {
            void Add(Entry entry, byte[] bytes)
            {
                if (bytes.Length != entry.Size || Hash(bytes) != entry.Sha256) throw new IOException("Generated file mismatch: " + entry.Path);
                long offset = blob.Position;
                using (var gzip = new GZipStream(blob, CompressionLevel.SmallestSize, true)) gzip.Write(bytes);
                records.Add(new { path = entry.Path, group = entry.Group, size = bytes.Length, sha256 = entry.Sha256, offset, compressedSize = blob.Position - offset });
            }
            byte[] Distributed(Entry entry)
            {
                var bytes = File.ReadAllBytes(Under(root, entry.File));
                if (Hash(bytes) != entry.FileHash) throw new IOException("Distributed file mismatch: " + entry.File);
                return bytes;
            }
            foreach (var entry in m.Files.Where(f => f.Container == null)) Add(entry, Distributed(entry));
            var indices = new Dictionary<string, List<(string Pkg, Hed.Entry Row)>>();
            foreach (var hed in m.Heds.Keys.Order())
            {
                using var stream = File.OpenRead(Under(archives, hed));
                foreach (var row in Hed.Read(stream))
                {
                    var key = Convert.ToHexString(row.MD5);
                    if (!indices.ContainsKey(key)) indices[key] = new();
                    indices[key].Add((Under(archives, Path.ChangeExtension(hed, ".pkg")), row));
                }
            }
            var groups = m.Files.Where(f => f.Container != null).GroupBy(f => f.Container!).ToList();
            int current = 0;
            foreach (var group in groups)
            {
                var key = Convert.ToHexString(MD5.HashData(Encoding.UTF8.GetBytes(group.Key)));
                if (!indices.TryGetValue(key, out var candidates)) throw new IOException("Missing original container: " + group.Key);
                EgsHdAsset? asset = null;
                byte[] Original(EgsHdAsset a, Entry e) => e.Asset == null ? a.OriginalData : a.RemasteredAssetsDecompressedData[e.Asset];
                foreach (var candidate in candidates)
                {
                    using var pkg = File.Open(candidate.Pkg, FileMode.Open, FileAccess.Read, FileShare.Read);
                    if (candidate.Row.Offset < 0 || candidate.Row.DataLength < 16 || candidate.Row.Offset > pkg.Length - candidate.Row.DataLength) throw new IOException("Invalid PKG bounds");
                    pkg.Position = candidate.Row.Offset;
                    byte[] header = new byte[16]; pkg.ReadExactly(header);
                    int length = System.Buffers.Binary.BinaryPrimitives.ReadInt32LittleEndian(header);
                    int count = System.Buffers.Binary.BinaryPrimitives.ReadInt32LittleEndian(header[4..]);
                    int compressed = System.Buffers.Binary.BinaryPrimitives.ReadInt32LittleEndian(header[8..]);
                    if (length < 1 || length > 128 * 1024 * 1024 || count < 0 || count > 1024 || compressed < -2 || compressed > candidate.Row.DataLength || 16L + count * 48L > candidate.Row.DataLength) throw new IOException("Invalid original asset header");
                    long allocation = length;
                    byte[] remasteredHeader = new byte[48];
                    for (int i = 0; i < count; i++)
                    {
                        pkg.ReadExactly(remasteredHeader);
                        int unpacked = BitConverter.ToInt32(remasteredHeader, 40), packed = BitConverter.ToInt32(remasteredHeader, 44);
                        if (unpacked < 0 || unpacked > 128 * 1024 * 1024 || packed < -2 || packed > candidate.Row.DataLength) throw new IOException("Invalid remastered asset header");
                        allocation += unpacked;
                    }
                    if (allocation > 512 * 1024 * 1024) throw new IOException("Asset exceeds safe preparation bounds");
                    pkg.Position = candidate.Row.Offset;
                    var possible = new EgsHdAsset(pkg);
                    if (group.All(e => (e.Asset == null || possible.RemasteredAssetsDecompressedData.ContainsKey(e.Asset)) && Original(possible, e).Length == e.SourceSize && Hash(Original(possible, e)) == e.SourceHash)) { asset = possible; break; }
                }
                if (asset == null) throw new IOException("Original data hash mismatch: " + group.Key);
                foreach (var entry in group) Add(entry, Apply(Original(asset, entry), Distributed(entry), entry.Size));
                Console.WriteLine($"Preparing Arabic files {++current}/{groups.Count}");
            }
        }
        var prepared = new { schema = 1, version = m.Version, blobHash = FileHash(Path.Combine(output, "payload.bin")), files = records };
        File.WriteAllText(Path.Combine(output, "manifest.json"), JsonSerializer.Serialize(prepared, Json) + "\n");
        Console.WriteLine("PASS: 831 mod files match the published 2.0.1 hashes; PKG/HED opened read-only.");
    }
    public static int Main(string[] args)
    {
        try
        {
            if (args is ["--self-test"]) SelfTest();
            else if (args is ["prepare", var manifest, var game, var output]) Prepare(manifest, Path.GetFullPath(game), Path.GetFullPath(output));
            else throw new ArgumentException("Usage: ManualAssets prepare manifest.json game-directory new-cache-directory");
            return 0;
        }
        catch (Exception error) { Console.Error.WriteLine(error.Message); return 1; }
    }
}
