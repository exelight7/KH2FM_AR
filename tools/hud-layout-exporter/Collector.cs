using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Web.Script.Serialization;
using System.Windows.Forms;

static class Collector {
    public const int MaxAsset = 8 * 1024 * 1024;
    public static readonly string[] Targets = {
        "field2d/us/he0command.2dd",
        "field2d/us/al0command.2dd",
        "field2d/us/bb0command.2dd",
        "field2d/us/ca0command.2dd",
        "field2d/us/dc0command.2dd",
        "field2d/us/dc1command.2dd",
        "field2d/us/di0command.2dd",
        "field2d/us/eh0command.2dd",
        "field2d/us/eh1command.2dd",
        "field2d/us/hb0command.2dd",
        "field2d/us/hb1command.2dd",
        "field2d/us/hb2command.2dd",
        "field2d/us/he1command.2dd",
        "field2d/us/lk0command.2dd",
        "field2d/us/mu0command.2dd",
        "field2d/us/nm0command.2dd",
        "field2d/us/nm1command.2dd",
        "field2d/us/tr0command.2dd",
        "field2d/us/tt0command.2dd",
        "field2d/us/tt1command.2dd",
        "field2d/us/tt2command.2dd",
        "field2d/us/tt3command.2dd",
        "field2d/us/tt4command.2dd",
        "field2d/us/tt5command.2dd",
        "field2d/us/tt6command.2dd",
        "field2d/us/wm0command.2dd",
        "field2d/us/zz0command.2dd"
    };
    public static string Hex(byte[] data) { return BitConverter.ToString(data).Replace("-", "").ToLowerInvariant(); }
    public static string Hash(byte[] data) { using (var hash=SHA256.Create()) return Hex(hash.ComputeHash(data)); }
    public static string NameHash(string name) { using (var hash=MD5.Create()) return Hex(hash.ComputeHash(Encoding.UTF8.GetBytes(name))); }
    static byte[] Exact(Stream stream, int length) {
        var bytes=new byte[length]; int offset=0;
        while(offset<length) { int read=stream.Read(bytes,offset,length-offset); if(read==0) throw new InvalidDataException("بيانات حزمة اللعبة ناقصة."); offset+=read; }
        return bytes;
    }
    // HED offsets refer to PKG headers. Only the original asset is read;
    // remastered image contents and unrelated package assets are skipped.
    public static byte[] Original(Stream pkg, long offset, int packedSize, int actualSize) {
        if(offset<0 || packedSize<16 || actualSize<=0 || actualSize>MaxAsset || offset>pkg.Length-packedSize)
            throw new InvalidDataException("حدود ملف التخطيط غير صالحة.");
        pkg.Position=offset; var header=Exact(pkg,16);
        int size=BitConverter.ToInt32(header,0), count=BitConverter.ToInt32(header,4), compressed=BitConverter.ToInt32(header,8);
        if(size!=actualSize || count<0 || count>1024 || compressed < -2 || compressed==0)
            throw new InvalidDataException("رأس ملف التخطيط غير صالح.");
        int stored=compressed>=0?compressed:size;
        long dataOffset=16L+count*48L;
        if(stored<=0 || stored>MaxAsset || dataOffset+stored>packedSize)
            throw new InvalidDataException("حجم ملف التخطيط غير صالح.");
        pkg.Position=offset+dataOffset; var data=Exact(pkg,stored);
        if(compressed>-2) PackageCrypto.Decode(header,data);
        if(compressed<0) return data;
        if(data.Length<6 || (data[0]&15)!=8 || (data[0]>>4)>7 || ((data[0]<<8)+data[1])%31!=0 || (data[1]&32)!=0)
            throw new InvalidDataException("ضغط ملف التخطيط غير صالح.");
        using(var input=new MemoryStream(data,2,data.Length-2))
        using(var inflate=new DeflateStream(input,CompressionMode.Decompress))
        using(var output=new MemoryStream(size)) {
            var buffer=new byte[8192]; int read;
            while((read=inflate.Read(buffer,0,buffer.Length))>0) {
                if(output.Length+read>size) throw new InvalidDataException("ملف التخطيط يتجاوز حجمه المعلن.");
                output.Write(buffer,0,read);
            }
            if(output.Length!=size) throw new InvalidDataException("فك ضغط ملف التخطيط غير مكتمل.");
            return output.ToArray();
        }
    }
    static bool Reparse(string file) { return (File.GetAttributes(file)&FileAttributes.ReparsePoint)!=0; }
    static IEnumerable<string> Packages(string dir,int depth) {
        if(depth>3 || Reparse(dir)) yield break;
        foreach(var file in Directory.GetFiles(dir,"*.hed"))
            if(Path.GetFileName(file).StartsWith("kh2",StringComparison.OrdinalIgnoreCase) && !Reparse(file)) yield return file;
        foreach(var sub in Directory.GetDirectories(dir))
            foreach(var file in Packages(sub,depth+1)) yield return file;
    }
    static void ValidateLayout(byte[] data) {
        if(data.Length<32 || BitConverter.ToUInt32(data,0)!=0x01524142)
            throw new InvalidDataException("الملف المستخرج ليس ملف تخطيط BAR صالحًا.");
        int count=BitConverter.ToInt32(data,4);
        if(count<=0 || count>1024 || 16L+count*16L>data.Length)
            throw new InvalidDataException("جدول ملف التخطيط غير صالح.");
    }
    public static void Export(string gameDir,string outputFile) {
        gameDir=Path.GetFullPath(gameDir); outputFile=Path.GetFullPath(outputFile);
        if(!File.Exists(Path.Combine(gameDir,"KINGDOM HEARTS II FINAL MIX.exe")))
            throw new InvalidDataException("اختر مجلد اللعبة الذي يحتوي KINGDOM HEARTS II FINAL MIX.exe.");
        if(outputFile.StartsWith(gameDir.TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("احفظ ملف الفحص خارج مجلد اللعبة، مثل سطح المكتب.");
        if(File.Exists(outputFile)) throw new IOException("الاسم موجود مسبقًا. اختر اسمًا جديدًا لملف الفحص.");
        string image=Path.Combine(gameDir,"Image");
        if(!Directory.Exists(image)) throw new InvalidDataException("لم أجد مجلد Image داخل مجلد اللعبة.");
        var names=Targets.ToDictionary(NameHash,x=>x);
        var assets=new Dictionary<string,byte[]>();
        var records=new List<object>(); int packageCount=0;
        foreach(var hed in Packages(image,0).OrderBy(x=>x,StringComparer.OrdinalIgnoreCase)) {
            if(++packageCount>128) throw new InvalidDataException("عدد حزم اللعبة غير متوقع.");
            var pkgName=Path.ChangeExtension(hed,"pkg");
            if(!File.Exists(pkgName) || Reparse(pkgName)) throw new InvalidDataException("حزمة اللعبة المقابلة لملف HED مفقودة.");
            using(var index=new FileStream(hed,FileMode.Open,FileAccess.Read,FileShare.Read))
            using(var pkg=new FileStream(pkgName,FileMode.Open,FileAccess.Read,FileShare.Read)) {
                if(index.Length%32!=0 || index.Length>64*1024*1024) throw new InvalidDataException("فهرس حزمة اللعبة غير صالح.");
                while(index.Position<index.Length) {
                    var entry=Exact(index,32); string name;
                    if(!names.TryGetValue(Hex(entry.Take(16).ToArray()),out name)) continue;
                    var bytes=Original(pkg,BitConverter.ToInt64(entry,16),BitConverter.ToInt32(entry,24),BitConverter.ToInt32(entry,28));
                    ValidateLayout(bytes);
                    if(assets.ContainsKey(name)) {
                        if(!assets[name].SequenceEqual(bytes)) throw new InvalidDataException("يوجد أكثر من تخطيط مختلف بالاسم نفسه؛ تعذر تحديد الأصل.");
                        continue;
                    }
                    assets.Add(name,bytes);
                    records.Add(new {path=name,size=bytes.Length,sha256=Hash(bytes),package=Path.GetFileName(hed)});
                }
            }
        }
        if(!assets.ContainsKey(Targets[0])) throw new InvalidDataException("لم أجد تخطيط القائمة المطلوب في حزم KH2. اختر مجلد اللعبة الصحيح ونسخة English.");
        var report=new {schema=1,tool="KH2FM HUD Layout Exporter 3",files=records,
            missing=Targets.Where(x=>!assets.ContainsKey(x)).ToArray()};
        string temporary=outputFile+"."+Guid.NewGuid().ToString("N")+".tmp";
        try {
            using(var stream=new FileStream(temporary,FileMode.CreateNew,FileAccess.Write))
            using(var zip=new ZipArchive(stream,ZipArchiveMode.Create)) {
                foreach(var pair in assets.OrderBy(x=>x.Key,StringComparer.Ordinal))
                    using(var file=zip.CreateEntry(pair.Key,CompressionLevel.Optimal).Open()) file.Write(pair.Value,0,pair.Value.Length);
                var json=new JavaScriptSerializer().Serialize(report);
                using(var writer=new StreamWriter(zip.CreateEntry("report.json").Open(),new UTF8Encoding(false))) writer.Write(json);
            }
            File.Move(temporary,outputFile);
        } finally { if(File.Exists(temporary)) File.Delete(temporary); }
    }
    [STAThread]
    public static int Main(string[] args) {
        try {
            if(args.Length==2 && args[0]=="--self-test") { Tests.Run(args[1]); return 0; }
            if(args.Length==3 && args[0]=="--export") { Export(args[1],args[2]); return 0; }
            if(args.Length!=0) throw new ArgumentException("استخدم الأداة بالنقر عليها مرتين.");
            Application.EnableVisualStyles();
            using(var folder=new FolderBrowserDialog {Description="اختر مجلد اللعبة الذي يحتوي KINGDOM HEARTS II FINAL MIX.exe",ShowNewFolderButton=false}) {
                if(folder.ShowDialog()!=DialogResult.OK) return 0;
                using(var save=new SaveFileDialog {Title="احفظ بيانات القائمة لإرسالها للفحص",Filter="ZIP|*.zip",FileName="KH2FM-HUD-Layout.zip",InitialDirectory=Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory)}) {
                    if(save.ShowDialog()!=DialogResult.OK) return 0;
                    Export(folder.SelectedPath,save.FileName);
                    MessageBox.Show("تم حفظ بيانات القائمة. أرسل ملف ZIP في المحادثة لإكمال ضبط موضع النص.","اكتمل جمع البيانات",MessageBoxButtons.OK,MessageBoxIcon.Information);
                }
            }
            return 0;
        } catch(Exception error) {
            if(args.Length==0) MessageBox.Show(error.Message,"تعذر جمع بيانات القائمة",MessageBoxButtons.OK,MessageBoxIcon.Error);
            else Console.Error.WriteLine(error);
            return 1;
        }
    }
}
