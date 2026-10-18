using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;

static class Tests {
    static int passed;
    static void Check(bool value,string name) { if(!value) throw new Exception(name); passed++; Console.WriteLine("PASS "+name); }
    static void Reject(Action action,string name) {
        bool rejected=false; try { action(); } catch(InvalidDataException) { rejected=true; } catch(IOException) { rejected=true; }
        Check(rejected,name);
    }
    static byte[] Fixture(string root,string name) {
        var index=File.ReadAllBytes(Path.Combine(root,name+".hed"));
        using(var pkg=File.OpenRead(Path.Combine(root,name+".pkg")))
            return Collector.Original(pkg,BitConverter.ToInt64(index,16),BitConverter.ToInt32(index,24),BitConverter.ToInt32(index,28));
    }
    static byte[] Bytes(string hex) { return Enumerable.Range(0,hex.Length/2).Select(i=>Convert.ToByte(hex.Substring(i*2,2),16)).ToArray(); }
    static Dictionary<string,string> Snapshot(string root) {
        return Directory.GetFiles(root,"*",SearchOption.AllDirectories).ToDictionary(x=>x,x=>Collector.Hash(File.ReadAllBytes(x)));
    }
    static void Same(Dictionary<string,string> before,string root,string name) {
        var after=Snapshot(root); Check(before.Count==after.Count && before.All(x=>after.ContainsKey(x.Key)&&after[x.Key]==x.Value),name);
    }
    static byte[] Bar() {
        var b=new byte[48]; Array.Copy(Encoding.ASCII.GetBytes("BAR\x01"),b,4);
        Array.Copy(BitConverter.GetBytes(1),0,b,4,4);
        Array.Copy(BitConverter.GetBytes(32),0,b,24,4);
        Array.Copy(BitConverter.GetBytes(16),0,b,28,4); return b;
    }
    static void MakeGame(string game) {
        string image=Path.Combine(game,"Image","en");Directory.CreateDirectory(image);
        File.WriteAllText(Path.Combine(game,"KINGDOM HEARTS II FINAL MIX.exe"),"unchanged game executable");
        File.WriteAllText(Path.Combine(game,"save.dat"),"unchanged save");
        using(var hed=new BinaryWriter(File.Create(Path.Combine(image,"kh2_first.hed"))))
        using(var pkg=new BinaryWriter(File.Create(Path.Combine(image,"kh2_first.pkg")))) {
            foreach(var name in Collector.Targets) {
                byte[] b=Bar();hed.Write(Bytes(Collector.NameHash(name)));hed.Write(pkg.BaseStream.Position);hed.Write(16+b.Length);hed.Write(b.Length);
                pkg.Write(b.Length);pkg.Write(0);pkg.Write(-2);pkg.Write(-1);pkg.Write(b);
            }
        }
    }
    public static void Run(string root) {
        Check(Collector.Targets.Length==27 && Collector.Targets.Contains("field2d/us/bb0command.2dd"),"all 27 layouts include the reported Beast Castle HUD");
        Check(Collector.NameHash("dummy.txt")=="e37e919dd0032e27c7e77add1c8b0cc5","OpenKH HED filename hash vector");
        Check(Encoding.ASCII.GetString(Fixture(root,"dummy"))=="COUCOU","OpenKH unencrypted original asset");
        Check(Encoding.ASCII.GetString(Fixture(root,"dummy_compressed_encrypted"))=="COUCOU","OpenKH encrypted compressed original asset");
        var raw=Fixture(root,"dummy_raw");Check(raw.Length==256 && Encoding.ASCII.GetString(raw,0,4)=="IMGD","OpenKH native image fixture");
        byte[] seed=Bytes("9094000000000000f02d0000831e4e60");
        var cipher=Bytes("bee9e894e9518b2e9edf9e69cc8b5579");PackageCrypto.Decode(seed,cipher);
        Check(Collector.Hex(cipher)=="789cb57d079c1445f67f754f0ebb3b9b","independent OpenKH decryption vector");
        var remasterIndex=File.ReadAllBytes(Path.Combine(root,"dummy_remastered.hed"));
        using(var pkg=File.OpenRead(Path.Combine(root,"dummy_remastered.pkg"))) {
            for(int i=0;i<remasterIndex.Length;i+=32) {
                var bytes=Collector.Original(pkg,BitConverter.ToInt64(remasterIndex,i+16),BitConverter.ToInt32(remasterIndex,i+24),BitConverter.ToInt32(remasterIndex,i+28));
                Check(bytes.Length==BitConverter.ToInt32(remasterIndex,i+28),"OpenKH remastered-header skip entry "+i/32);
            }
        }
        byte[] valid=File.ReadAllBytes(Path.Combine(root,"dummy.pkg"));
        Reject(()=>{using(var p=new MemoryStream(valid))Collector.Original(p,-1,22,6);},"negative package offset rejected");
        Reject(()=>{using(var p=new MemoryStream(valid))Collector.Original(p,long.MaxValue,22,6);},"overflowing package offset rejected");
        Reject(()=>{using(var p=new MemoryStream(valid))Collector.Original(p,0,23,6);},"truncated package rejected");
        Reject(()=>{using(var p=new MemoryStream(valid))Collector.Original(p,0,22,Collector.MaxAsset+1);},"oversized original rejected before allocation");
        Reject(()=>{using(var p=new MemoryStream(valid))Collector.Original(p,0,22,5);},"HED/header length mismatch rejected");
        byte[] bad=(byte[])valid.Clone();Array.Copy(BitConverter.GetBytes(1025),0,bad,4,4);
        Reject(()=>{using(var p=new MemoryStream(bad))Collector.Original(p,0,22,6);},"oversized remastered table rejected");
        bad=(byte[])valid.Clone();Array.Copy(BitConverter.GetBytes(-3),0,bad,8,4);
        Reject(()=>{using(var p=new MemoryStream(bad))Collector.Original(p,0,22,6);},"unknown compression mode rejected");
        bad=(byte[])valid.Clone();Array.Copy(BitConverter.GetBytes(Collector.MaxAsset+1),0,bad,8,4);
        Reject(()=>{using(var p=new MemoryStream(bad))Collector.Original(p,0,22,6);},"oversized compressed input rejected before allocation");
        string temporary=Path.Combine(Path.GetTempPath(),"kh2-hud-export-test-"+Guid.NewGuid().ToString("N"));Directory.CreateDirectory(temporary);
        try {
            string game=Path.Combine(temporary,"Game"),output=Path.Combine(temporary,"layout.zip");MakeGame(game);var before=Snapshot(game);
            Collector.Export(game,output);
            using(var z=ZipFile.OpenRead(output)) {
                Check(z.Entries.Select(x=>x.FullName).OrderBy(x=>x).SequenceEqual(Collector.Targets.Concat(new[]{"report.json"}).OrderBy(x=>x)),"export contains only the requested world layouts and report");
                foreach(var name in Collector.Targets)using(var s=z.GetEntry(name).Open())using(var m=new MemoryStream()) {s.CopyTo(m);Check(m.ToArray().SequenceEqual(Bar()),"exported layout bytes "+name);}
                using(var reader=new StreamReader(z.GetEntry("report.json").Open())) {
                    string report=reader.ReadToEnd();Check(!report.Contains(game) && !report.Contains(Environment.UserName),"report excludes game path and account name");
                }
            }
            Same(before,game,"all game and save files unchanged after successful export");
            string zipHash=Collector.Hash(File.ReadAllBytes(output));Reject(()=>Collector.Export(game,output),"existing output is not overwritten");
            Check(zipHash==Collector.Hash(File.ReadAllBytes(output)),"existing output bytes preserved");
            Reject(()=>Collector.Export(game,Path.Combine(game,"export.zip")),"output inside game folder rejected");
            Same(before,game,"game unchanged after rejected in-game output");
            byte[] index=File.ReadAllBytes(Path.Combine(game,"Image/en/kh2_first.hed"));index[0]^=255;File.WriteAllBytes(Path.Combine(game,"Image/en/kh2_first.hed"),index);before=Snapshot(game);
            string missing=Path.Combine(temporary,"missing.zip");Reject(()=>Collector.Export(game,missing),"missing required layout rejected");
            Check(!File.Exists(missing),"no incomplete ZIP on failure");Same(before,game,"game unchanged after failed export");
            Check(Directory.GetFiles(temporary,"*.tmp",SearchOption.AllDirectories).Length==0,"temporary exports cleaned up");
        } finally {Directory.Delete(temporary,true);}
        File.WriteAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory,"SELF_TEST.json"), "{\"passed\":true,\"checks\":"+passed+",\"realGameTested\":false}");
        Console.WriteLine("Passed "+passed+" checks");
    }
}
