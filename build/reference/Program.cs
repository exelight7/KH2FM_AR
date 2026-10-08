using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Drawing.Text;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Runtime.Loader;
using System.Security.Cryptography;
using System.Text;

static class P
{
    const string Apps = @"<OPENKH_DIR>\Apps";
    public static Assembly Kh2;
    public static object Enc;
    public static MethodInfo DecodeM;

    public static void Init()
    {
        AssemblyLoadContext.Default.Resolving += (ctx, name) =>
        {
            var c = Path.Combine(Apps, name.Name + ".dll");
            return File.Exists(c) ? ctx.LoadFromAssemblyPath(c) : null;
        };
        Kh2 = AssemblyLoadContext.Default.LoadFromAssemblyPath(Path.Combine(Apps, "OpenKh.Kh2.dll"));
        var encs = Kh2.GetType("OpenKh.Kh2.Messages.Encoders");
        Enc = encs.GetProperty("InternationalSystem", BindingFlags.Public | BindingFlags.Static).GetValue(null);
        DecodeM = Enc.GetType().GetMethod("Decode");
    }

    public static object BarRead(string path)
    {
        var t = Kh2.GetType("OpenKh.Kh2.Bar");
        var m = t.GetMethod("Read", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(Stream) }, null);
        using var fs = File.OpenRead(path);
        return m.Invoke(null, new object[] { fs });
    }

    public static List<object> MsgRead(Stream s)
    {
        var t = Kh2.GetType("OpenKh.Kh2.Msg");
        var m = t.GetMethod("Read", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(Stream) }, null);
        return ((System.Collections.IEnumerable)m.Invoke(null, new object[] { s })).Cast<object>().ToList();
    }

    public static List<object> Decode(byte[] data) =>
        ((System.Collections.IEnumerable)DecodeM.Invoke(Enc, new object[] { data })).Cast<object>().ToList();

    public static string Cmd(object m) => m.GetType().GetProperty("Command").GetValue(m)?.ToString();
    public static byte[] Data(object m) => m.GetType().GetProperty("Data").GetValue(m) as byte[];
    public static string Text(object m) => m.GetType().GetProperty("Text").GetValue(m)?.ToString();

    /// <summary>Read bar, replace one entry's stream, write bar; then verify other entries untouched.</summary>
    public static void BarReplace(string src, string dst, string entryName, byte[] data)
    {
        var t = Kh2.GetType("OpenKh.Kh2.Bar");
        object bar;
        using (var fs = File.OpenRead(src))
            bar = t.GetMethod("Read", new[] { typeof(Stream) }).Invoke(null, new object[] { fs });
        bool found = false;
        foreach (var e in (System.Collections.IEnumerable)bar)
        {
            if ((string)e.GetType().GetProperty("Name").GetValue(e) == entryName)
            {
                e.GetType().GetProperty("Stream").SetValue(e, new MemoryStream(data));
                found = true;
            }
        }
        if (!found) throw new Exception($"entry '{entryName}' not found in {src}");
        using var ofs = File.Create(dst);
        t.GetMethod("Write", new[] { typeof(Stream), t }).Invoke(null, new object[] { ofs, bar });
    }

    /// <summary>Entry names + stream bytes of a bar (for verification).</summary>
    public static List<(string name, byte[] data)> BarEntries(string path)
    {
        var t = Kh2.GetType("OpenKh.Kh2.Bar");
        object bar;
        using (var fs = File.OpenRead(path))
            bar = t.GetMethod("Read", new[] { typeof(Stream) }).Invoke(null, new object[] { fs });
        var res = new List<(string, byte[])>();
        foreach (var e in (System.Collections.IEnumerable)bar)
        {
            var s = (Stream)e.GetType().GetProperty("Stream").GetValue(e);
            s.Position = 0;
            using var ms = new MemoryStream();
            s.CopyTo(ms);
            res.Add(((string)e.GetType().GetProperty("Name").GetValue(e), ms.ToArray()));
        }
        return res;
    }
}

// ---------- Arabic inventory: letter -> join class, and its Presentation-Form codepoints ----------
enum JC { D, R, U }   // dual-joining, right-joining, non-joining

static class Ar
{
    public static readonly Dictionary<char, JC> Join = new()
    {
        ['ب']=JC.D,['ت']=JC.D,['ث']=JC.D,['ج']=JC.D,['ح']=JC.D,['خ']=JC.D,
        ['س']=JC.D,['ش']=JC.D,['ص']=JC.D,['ض']=JC.D,['ط']=JC.D,['ظ']=JC.D,
        ['ع']=JC.D,['غ']=JC.D,['ف']=JC.D,['ق']=JC.D,['ك']=JC.D,['ل']=JC.D,
        ['م']=JC.D,['ن']=JC.D,['ه']=JC.D,['ي']=JC.D,['ئ']=JC.D,
        ['ا']=JC.R,['د']=JC.R,['ذ']=JC.R,['ر']=JC.R,['ز']=JC.R,['و']=JC.R,
        ['ة']=JC.R,['أ']=JC.R,['إ']=JC.R,['آ']=JC.R,['ؤ']=JC.R,['ى']=JC.R,
        ['ء']=JC.U,
    };

    // base letter -> [isolated, final, initial, medial]  (missing => that form does not exist)
    public static readonly Dictionary<char, int[]> Pf = new()
    {
        ['ء'] = new[]{0xFE80},
        ['آ'] = new[]{0xFE81,0xFE82},
        ['أ'] = new[]{0xFE83,0xFE84},
        ['إ'] = new[]{0xFE87,0xFE88},
        ['ؤ'] = new[]{0xFE85,0xFE86},
        ['ئ'] = new[]{0xFE89,0xFE8A,0xFE8B,0xFE8C},
        ['ا'] = new[]{0xFE8D,0xFE8E},
        ['ب'] = new[]{0xFE8F,0xFE90,0xFE91,0xFE92},
        ['ة'] = new[]{0xFE93,0xFE94},
        ['ت'] = new[]{0xFE95,0xFE96,0xFE97,0xFE98},
        ['ث'] = new[]{0xFE99,0xFE9A,0xFE9B,0xFE9C},
        ['ج'] = new[]{0xFE9D,0xFE9E,0xFE9F,0xFEA0},
        ['ح'] = new[]{0xFEA1,0xFEA2,0xFEA3,0xFEA4},
        ['خ'] = new[]{0xFEA5,0xFEA6,0xFEA7,0xFEA8},
        ['د'] = new[]{0xFEA9,0xFEAA},
        ['ذ'] = new[]{0xFEAB,0xFEAC},
        ['ر'] = new[]{0xFEAD,0xFEAE},
        ['ز'] = new[]{0xFEAF,0xFEB0},
        ['س'] = new[]{0xFEB1,0xFEB2,0xFEB3,0xFEB4},
        ['ش'] = new[]{0xFEB5,0xFEB6,0xFEB7,0xFEB8},
        ['ص'] = new[]{0xFEB9,0xFEBA,0xFEBB,0xFEBC},
        ['ض'] = new[]{0xFEBD,0xFEBE,0xFEBF,0xFEC0},
        ['ط'] = new[]{0xFEC1,0xFEC2,0xFEC3,0xFEC4},
        ['ظ'] = new[]{0xFEC5,0xFEC6,0xFEC7,0xFEC8},
        ['ع'] = new[]{0xFEC9,0xFECA,0xFECB,0xFECC},
        ['غ'] = new[]{0xFECD,0xFECE,0xFECF,0xFED0},
        ['ف'] = new[]{0xFED1,0xFED2,0xFED3,0xFED4},
        ['ق'] = new[]{0xFED5,0xFED6,0xFED7,0xFED8},
        ['ك'] = new[]{0xFED9,0xFEDA,0xFEDB,0xFEDC},
        ['ل'] = new[]{0xFEDD,0xFEDE,0xFEDF,0xFEE0},
        ['م'] = new[]{0xFEE1,0xFEE2,0xFEE3,0xFEE4},
        ['ن'] = new[]{0xFEE5,0xFEE6,0xFEE7,0xFEE8},
        ['ه'] = new[]{0xFEE9,0xFEEA,0xFEEB,0xFEEC},
        ['و'] = new[]{0xFEED,0xFEEE},
        ['ى'] = new[]{0xFEEF,0xFEF0},
        ['ي'] = new[]{0xFEF1,0xFEF2,0xFEF3,0xFEF4},
    };

    public const int ISO = 0, FIN = 1, INI = 2, MED = 3;

    /// <summary>form index for a letter given whether it joins to logical-prev / logical-next</summary>
    public static int Form(char c, bool joinPrev, bool joinNext)
    {
        var cls = Join[c];
        bool jp = cls != JC.U && joinPrev;
        bool jn = cls == JC.D && joinNext;
        if (jp && jn) return MED;
        if (jp) return FIN;
        if (jn) return INI;
        return ISO;
    }

    public static bool JoinsPrev(char c) => Join[c] != JC.U;   // can touch its logical predecessor
    public static bool JoinsNext(char c) => Join[c] == JC.D;

    public static bool IsArabic(char c) => Join.ContainsKey(c);

    public static IEnumerable<(char letter, int form)> Needed()
    {
        foreach (var kv in Join)
            for (int f = 0; f < Pf[kv.Key].Length; f++)
                yield return (kv.Key, f);
    }
}

static class Program
{
    // cell geometry of the ACTIVE atlas. Defaults = sys; BuildEvt() switches them to evt
    // (21x16 grid of 12x32 cells) for the whole lifetime of the process, which is safe
    // because Main dispatches exactly one command per run.
    static int COLS = 28, ROWS = 10, CW = 9, CH = 24;
    const string Root = @"<PROJECT_DIR>";
    // Full-opacity glyph level of the retail atlases: evt.rgb max = 51 (0x33) and the core band
    // 33..64 peaks at 51x5762; the latin A,B,C cells peak at 51 as well.  0x32 was one level low.
    const byte Ink = 0x33;

    // P3 (see PROJECT_STATE.md, section P3): digits must keep >=1px of air when a
    // number sits directly beside an Arabic glyph. The base game's digit metrics have
    // zero right bearing (k = sp - 2w = 0 for '0','2'-'9'), which was never visible
    // because the original English text never puts a letter after a digit. In Arabic it
    // happens all the time, e.g. player name "روكساس" + level "5": the visual order is
    // [5][س ISO] so cell 117 ('5') is what separates the number from the name, and with
    // sp = 10 the gap was exactly 0px (touching). sp is in half-pixels (advance = sp/2),
    // so +2 sp = +1px advance. Cells 112-121 = '0'-'9'. Arabic cells and every other
    // latin cell keep their own values.
    const int DigitCellFirst = 112, DigitCellLast = 121;
    const int DigitSpBoost = 2;

    // ---- message control-byte grammar (shared by `batch`, `dump` and `preflight`) ----
    // operand count per control byte. Empirically validated on sys.bar: 3356/3357 messages parse
    // from index 0 to exactly their final 0x00 terminator (only dev junk id1446 fails) — in sys.bar
    // no byte <0x20 outside the entries above ever appears in command position.
    static readonly Dictionary<byte, int> MsgCmdSize = new() {
        {0x01,0},{0x02,0},{0x03,0},{0x06,1},{0x07,4},{0x08,3},{0x09,1},{0x0A,1},{0x0B,1},
        {0x0C,0},{0x0D,0},{0x0E,1},{0x10,0},{0x11,4},{0x13,4},{0x14,2},
        // World bars only (absent from sys.bar, so sys behaviour is unchanged). Operand counts
        // read off OpenKh InternationalSystemDecode._table (DataCmdModel/SingleDataCmdModel/
        // TableCmdModel Length) + openkh.dev/kh2/file/type/msg.html for the names:
        {0x04,1},   // Theme           — 1 byte palette index ("color defined in the world palette")
        {0x0F,5},   // Unknown0f       — DataCmdModel(..., 5)
        {0x12,2},   // Unknown12       — DataCmdModel(..., 2)
        {0x15,2},   // CharDelay       — 2 bytes ("delay, in frames, for every character")
        {0x16,1},   // Unknown16       — SingleDataCmdModel
        {0x17,2},   // DelayAndFade    — 2 bytes ("delay + make the text fade away")
        {0x18,2},   // Unknown18       — DataCmdModel(..., 2)
        {0x1A,1},   // Table3          — 1 byte ("use the 3rd font table for the next character")
        {0x1B,1},   // Table4          — 1 byte ("use the 4th font table for the next character")
        {0x1C,1},   // Table5          — 1 byte ("use the 5th font table for the next character")
        // NOT added (documented by OpenKh, never observed in sys.bar or tt.bar): 0x05 (6 bytes),
        // 0x19/0x1D/0x1E/0x1F (1 byte, font tables 2/6/7/8) — added only if seen.
        // 0x06/0x08/0x0A/0x13 operand counts above were corrected from OpenKh's own decoder
        // output (OpenKh prints opcode+1, operands verbatim): sys 1444 "<0B 0E>" = raw 0A 0E,
        // sys 1446 "<14 FA 00 64 00><09 01 00 07>" = raw 13 FA 00 64 00 / 08 01 00 07,
        // tt 12157 "<14 82 00 46 00><07 00><09 01 01 05>" = raw 13.. / 06 00 / 08 01 01 05.
        // Without this, 189 tt.bar messages fail to decode ("interior End 0x00 in text span")
        // and sys id 1446 fails too; sys decode is otherwise byte-identical (verified).
    };
    static bool MsgIsCmd(byte b) => b < 0x20 && b != 0x00 && b != 0x01 && b != 0x02;
    static int MsgHexVal(char c) => c >= '0' && c <= '9' ? c - '0' : c >= 'A' && c <= 'F' ? c - 'A' + 10
                                  : c >= 'a' && c <= 'f' ? c - 'a' + 10 : -1;

    // "<C 09 DB>" / "<C 07 FF 00 00 80>" — uppercase hex, space separated
    static string MsgCmdToken(byte[] m, int i)
    {
        if (!MsgCmdSize.TryGetValue(m[i], out var n)) throw new Exception($"no size for command 0x{m[i]:X2}");
        if (i + n >= m.Length) throw new Exception($"truncated command 0x{m[i]:X2}");
        var sb = new StringBuilder("<C ");
        sb.Append(m[i].ToString("X2"));
        for (int k = 1; k <= n; k++) sb.Append(' ').Append(m[i + k].ToString("X2"));
        sb.Append('>');
        return sb.ToString();
    }

    static bool MsgTryToken(string s, int pos, out int len, out byte[] raw)
    {
        len = 0; raw = null;
        if (pos + 3 > s.Length || s[pos] != '<' || s[pos + 1] != 'C' || s[pos + 2] != ' ') return false;
        int gt = s.IndexOf('>', pos + 3);
        if (gt < 0) return false;
        var bl = new List<byte>();
        foreach (var p in s.Substring(pos + 3, gt - pos - 3).Split(' '))
        {
            if (p.Length != 2 || MsgHexVal(p[0]) < 0 || MsgHexVal(p[1]) < 0) return false;
            bl.Add((byte)(MsgHexVal(p[0]) * 16 + MsgHexVal(p[1])));
        }
        if (bl.Count == 0 || !MsgCmdSize.TryGetValue(bl[0], out var n) || bl.Count != n + 1) return false;
        raw = bl.ToArray(); len = gt - pos + 1;
        return true;
    }

    // "<X 55>" = raw cell byte for cells with no single-char original mapping
    // (multi-char GLYPHs like 85='II', 94='XIII', and FORBIDDEN cells 82/83)
    static string MsgCellToken(int cell) => $"<X {cell:X2}>";
    static bool MsgTryCellToken(string s, int pos, out int len, out int cell)
    {
        len = 0; cell = -1;
        if (pos + 4 > s.Length || s[pos] != '<' || s[pos + 1] != 'X' || s[pos + 2] != ' ') return false;
        int gt = s.IndexOf('>', pos + 3);
        if (gt < 0 || gt - pos - 3 != 2) return false;
        int a = MsgHexVal(s[pos + 3]), b = MsgHexVal(s[pos + 4]);
        if (a < 0 || b < 0) return false;
        cell = a * 16 + b;
        if (cell > 279) return false;
        len = gt - pos + 1;
        return true;
    }

    // decode [start,end) of a message body to text, emitting <C ...> for control bytes
    static string MsgDecodeEn(byte[] bytes, int start, int end, Dictionary<int, char> cellToChar)
    {
        var sb = new StringBuilder();
        int i = start;
        while (i < end)
        {
            byte b = bytes[i];
            if (b == 0x01) { sb.Append(' '); i++; continue; }
            if (b == 0x02) { sb.Append('\n'); i++; continue; }
            if (b == 0x00) throw new Exception("interior End 0x00 in text span");
            if (MsgIsCmd(b))
            {
                if (!MsgCmdSize.TryGetValue(b, out var n)) throw new Exception($"unknown command 0x{b:X2} in text span");
                if (i + n >= end) throw new Exception($"truncated command 0x{b:X2}");
                sb.Append(MsgCmdToken(bytes, i));
                i += n + 1;
                continue;
            }
            if (!cellToChar.TryGetValue(b - 0x20, out var ch))
                sb.Append(MsgCellToken(b - 0x20));
            else
                sb.Append(ch);
            i++;
        }
        return sb.ToString();
    }

    // skip leading control bytes; returns text span start
    static int MsgSkipLeading(byte[] m)
    {
        int i = 0;
        while (i < m.Length && MsgIsCmd(m[i]))
        {
            if (!MsgCmdSize.TryGetValue(m[i], out var n)) throw new Exception($"unknown leading command 0x{m[i]:X2}");
            i += 1 + n;
            if (i > m.Length - 1) throw new Exception("truncated command prefix");
        }
        return i;
    }

    static int Main(string[] args)
    {
        try { Console.OutputEncoding = System.Text.Encoding.UTF8; } catch { }
        P.Init();
        switch (args.Length > 0 ? args[0] : "help")
        {
            case "map": return Map();
            case "probe": return Probe();
            case "preview": return Preview();
            case "alloc": return Alloc();
            case "build": return Build();
            case "buildevt": return BuildEvt(args.Length > 1 ? int.Parse(args[1]) : 21,
                                             args.Length <= 2 || args[2] != "0");
            case "previewevt": return PreviewEvt(args.Length > 1 ? int.Parse(args[1]) : 21);
            case "rt": return Rt();
            case "batch": return Batch(args.Length > 1 ? args[1] : null);
            case "batchtt": return BatchTt(args.Length > 1 ? args[1] : null, args.Length > 2 ? args[2] : null, args.Length > 3 ? args[3] : null, args.Length > 4 ? args[4] : null);
            case "dump": return Dump(args.Length > 1 ? args[1] : null, args.Length > 2 ? args[2] : null);
            case "preflight": return PreFlight(args.Length > 1 ? args[1] : null, args.Length > 2 ? args[2] : null);
            case "bardump": return BarDump(args.Length > 1 ? args[1] : null);
            case "inject": return Inject(args.Length > 4 ? args[1] : null, args.Length > 2 ? args[2] : "0",
                                         args.Length > 3 ? args[3] : null, args.Length > 4 ? args[4] : null);
            case "help":
            default:
                Console.WriteLine("usage: map | probe | preview | alloc | build | buildevt [size] [ext=0] | previewevt [size] | rt | batch [tsv] | batchtt [tsv] | dump <ids> [bar] | preflight [tsv] [bar] | bardump <file.bar> | inject <bar> <id> <ar.txt> <out.bar>");
                return 1;
        }
    }

    // ================= evt atlas (tt.bar cutscene text is drawn with the evt font) =============
    // geometry: 21 cols x 16 rows of 12x32 cells, image 256x512 @8bit = 131072 B, evt.list=336.
    // cell index is the SAME as sys (cell = code - 0x20) - verified: same-index IoU 0.533 vs
    // 0.415 shifted control, corr(evt.list, sys.list)=0.877, corr(ink widths)=0.883, and
    // rendering the cells of "THE USUAL PLACE"/"Attack"/"Save"/"Load" out of evt.rgb spells them.
    const int E_COLS = 21, E_ROWS = 16, E_CW = 12, E_CH = 32;
    const int E_STRIDE = 256, E_RGBLEN = 131072, E_LISTLEN = 336;
    // retail evt baseline = modal bottom-of-ink over non-descending latin cells (measured: 28,
    // sys equivalent is 20).  Used to align our drawn baseline with the kept latin cells.
    const int E_RetailBaseline = 28;
    static readonly string ModMsgDir =
        @"<OPENKH_DIR>\mod\kh2\msg\us";

    // ---- font-comparison hooks (BUILD-ONLY; defaults = old behaviour, installed files are never written) ----
    // KH2_FONT_FILE   ttf to draw the Arabic with instead of the system "Segoe UI" Bold
    // KH2_EVT_OUT     output dir of buildevt (default font-rtl\arabic\out\evt)
    // KH2_EVT_SRCDIR  dir holding the fontimage.bar/fontinfo.bar whose evt entry is retail (default = the mod dir)
    // KH2_ISO_BASE=1  draw ISO presentation forms from the base letter (fonts without U+FE80..FEFC isolated forms, e.g. Cairo)
    static readonly string FontFile = Environment.GetEnvironmentVariable("KH2_FONT_FILE");
    // font-test: KH2_SEP_ADJ=-2 shrinks the ISO/INI separation advance by 1px (evt only; default 0 = unchanged)
    static readonly bool SepIniOnly = Environment.GetEnvironmentVariable("KH2_SEP_INI_ONLY") == "1";   // adjust INI cells only (ISO->Latin pairs need the full gap)
    static readonly int SepAdj = int.TryParse(Environment.GetEnvironmentVariable("KH2_SEP_ADJ"), out var sepAdj0) ? sepAdj0 : 0;
    static readonly string EvtOut = Environment.GetEnvironmentVariable("KH2_EVT_OUT") ?? Path.Combine(Root, @"font-rtl\arabic\out\evt");
    static readonly string EvtSrcDir = Environment.GetEnvironmentVariable("KH2_EVT_SRCDIR");
    static readonly bool IsoBase = Environment.GetEnvironmentVariable("KH2_ISO_BASE") == "1";
    static System.Drawing.Text.PrivateFontCollection _pfc;
    static string FontLabel => string.IsNullOrEmpty(FontFile) ? "Segoe UI" : Path.GetFileNameWithoutExtension(FontFile);
    static Font MakeFont(float px)
    {
        if (string.IsNullOrEmpty(FontFile)) return new Font("Segoe UI", px, FontStyle.Bold, GraphicsUnit.Pixel);
        if (_pfc == null) { _pfc = new System.Drawing.Text.PrivateFontCollection(); _pfc.AddFontFile(FontFile); }
        var fam = _pfc.Families[0];
        return new Font(fam, px, fam.IsStyleAvailable(FontStyle.Bold) ? FontStyle.Bold : FontStyle.Regular, GraphicsUnit.Pixel);
    }
    static Dictionary<int, char> _isoBase;
    static char GlyphChar(int cp)
    {
        if (!IsoBase) return (char)cp;
        if (_isoBase == null)
        {
            _isoBase = new Dictionary<int, char>();
            foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\allocation.tsv")).Skip(1))
            {
                var q = line.Split('\t');
                if (q.Length >= 5 && q[3] == "ISO") _isoBase[Convert.ToInt32(q[1], 16)] = q[0][0];
            }
        }
        return _isoBase.TryGetValue(cp, out var bc) ? bc : (char)cp;
    }

    // ---- lam-alef ligature (evt atlas / tt.bar ONLY; sys atlas and sys.bar never use it) ----
    // One reserve Latin cell of the evt atlas (cell 36 = 'W', unused by every translation) carries the ISOLATED
    // ligature U+FEFB.  allocation.tsv is NOT changed; the single extra row lives in allocation_lamalef_evt.tsv.
    // Used by `buildevt` (draws it) and `batchtt` (encodes lam-INI + alef-FIN to it).  KH2_LAMALEF=0 = old behaviour.
    static readonly string LamAlefFile = Path.Combine(Root, Environment.GetEnvironmentVariable("KH2_LAMALEF2") == "1" ? @"font-rtl\arabic\allocation_lamalef2_evt.tsv" : @"font-rtl\arabic\allocation_lamalef_evt.tsv");   // lamalef2 = + final-form ligature (cell 33)
    static readonly bool LamAlefOn = Environment.GetEnvironmentVariable("KH2_LAMALEF") != "0" && File.Exists(LamAlefFile);
    static List<(char letter, int form, string formName, int cell, int code, string pf)> LamAlefRows()
    {
        var rows = new List<(char, int, string, int, int, string)>();
        foreach (var line in File.ReadLines(LamAlefFile).Skip(1))
        {
            var q = line.Split('\t');
            if (q.Length >= 6) rows.Add((q[0][0], int.Parse(q[2]), q[3], int.Parse(q[4]), Convert.ToInt32(q[5], 16), q[1]));
        }
        return rows;
    }

    static (int l, int r, int t, int b) BoxOf(byte[] rgb, int cell, int cols, int cw, int ch, byte minInk = 1)
    {
        int x0 = (cell % cols) * cw, y0 = (cell / cols) * ch;
        int l = int.MaxValue, r = -1, t = int.MaxValue, b = -1;
        for (int y = 0; y < ch; y++)
            for (int x = 0; x < cw; x++)
                if (rgb[(y0 + y) * E_STRIDE + (x0 + x)] >= minInk)
                { if (x < l) l = x; if (x > r) r = x; if (y < t) t = y; if (y > b) b = y; }
        if (r < 0) return (0, -1, 0, -1);
        return (l, r, t, b);
    }

    static Dictionary<int, string> LoadFormNames()
    {
        var d = new Dictionary<int, string>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\allocation.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length >= 5) d[int.Parse(p[4])] = p[3];
        }
        return d;
    }

    static Dictionary<char, int> LoadCharCell()
    {
        var d = new Dictionary<char, int>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length < 11 || p[1] == "-") continue;
            if (p[10] != "GLYPH" || p[5].Length != 1) continue;
            int cell = int.Parse(p[1]);
            if (cell >= 0) d[p[5][0]] = cell;
        }
        return d;
    }

    /// <summary>Drop &lt;C xx xx xx&gt; state commands and line breaks so the layout
    /// simulator only sees printable text (the encoder consumes commands separately).</summary>
    static string StripCommands(string s)
    {
        var sb = new StringBuilder(s.Length);
        for (int i = 0; i < s.Length; i++)
        {
            if (s[i] == '<')
            {
                int j = s.IndexOf('>', i + 1);
                if (j > i)
                {
                    var seg = s.Substring(i + 1, j - i - 1);
                    bool ok = seg.Length >= 1 && seg.Length <= 14
                              && seg[0] is >= 'A' and <= 'Z'
                              && seg.All(c => c is (>= 'A' and <= 'Z') or (>= '0' and <= '9') or ' ');
                    if (ok) { i = j; continue; }
                }
            }
            if (s[i] == '\\' && i + 1 < s.Length && s[i + 1] == 'n') { i++; sb.Append(' '); continue; }
            sb.Append(s[i] == '\n' || s[i] == '\r' || s[i] == '\t' ? ' ' : s[i]);
        }
        return System.Text.RegularExpressions.Regex.Replace(sb.ToString(), " {2,}", " ").Trim();
    }

    static List<string> LoadWords(params string[] rel)
    {
        var res = new List<string>();
        foreach (var r in rel)
        {
            var p = Path.Combine(Root, r);
            if (!File.Exists(p)) continue;
            foreach (var line in File.ReadLines(p))
            {
                var q = line.Split('\t');
                if (q.Length >= 3 && q[2].Trim().Length > 0) res.Add(StripCommands(q[2].Trim()));
            }
        }
        return res.Where(w => w.Length > 0).Distinct().ToList();
    }

    /// <summary>
    /// Layout simulator: the engine draws each glyph's cell ink at offset l and advances by
    /// sp/2 (SD px).  gap = adv_left + l_right - (r_left + 1).
    /// weld (left glyph is Arabic MED/FIN) must be &lt;= 0, separation must be &gt;= +1.
    /// Boxes are measured on CORE ink (>= 33 of 0..255): retail atlases carry a low-value
    /// antialiasing fringe (values 1 and 16..19) that overlaps ~1px between retail Latin
    /// neighbours without being visible; measuring it would make retail's own text fail.
    /// Mirrors font-rtl\joinfix PairTable() so the numbers stay comparable.
    /// </summary>
    static (int pairs, int broken, List<string> lines) GapTable(
        string label, byte[] rgb, byte[] list, int cols, int cw, int ch,
        Dictionary<int, string> formName, Dictionary<char, int> charCell, List<string> words)
    {
        const byte Core = 33;
        var lines = new List<string>();
        int pairs = 0, broken = 0, brokenWeld = 0, brokenSep = 0;
        int weldN = 0, weldOk = 0; int minWeld = int.MaxValue, maxSep = int.MinValue, minSep = int.MaxValue;
        int arAr = 0, mixed = 0, latLat = 0;
        var hist = new SortedDictionary<int, int>();
        foreach (var word in words)
        {
            var vis = ToVisual(Shape(word));
            for (int i = 0; i + 1 < vis.Count; i++)
            {
                var (cl, fl, _) = vis[i];
                var (cr, fr, _) = vis[i + 1];
                if (cl == ' ' || cr == ' ') continue;
                int cellL, cellR;
                if (fl >= 0) { if (!TryArabicCell(cl, fl, out cellL)) continue; }
                else if (!charCell.TryGetValue(cl, out cellL)) continue;
                if (fr >= 0) { if (!TryArabicCell(cr, fr, out cellR)) continue; }
                else if (!charCell.TryGetValue(cr, out cellR)) continue;
                var bL = BoxOf(rgb, cellL, cols, cw, ch, Core);
                var bR = BoxOf(rgb, cellR, cols, cw, ch, Core);
                if (bL.r < 0 || bR.r < 0) continue;
                float advL = list[cellL] / 2f;
                int gap = (int)Math.Round(advL + bR.l - (bL.r + 1));
                bool weld = fl >= 0 && formName.TryGetValue(cellL, out var fn) && fn is "MED" or "FIN";
                bool ok = weld ? gap <= 0 : gap > 0;
                pairs++;
                hist[gap] = hist.TryGetValue(gap, out var hn) ? hn + 1 : 1;
                if (fl >= 0 && fr >= 0) arAr++; else if (fl < 0 && fr < 0) latLat++; else mixed++;
                if (!ok) { broken++; if (weld) brokenWeld++; else brokenSep++; }
                if (weld) { weldN++; if (gap <= 0) weldOk++; minWeld = Math.Min(minWeld, gap); }
                else { maxSep = Math.Max(maxSep, gap); minSep = Math.Min(minSep, gap); }
                lines.Add($"{label}\t{word}\t{cl}{(fl >= 0 ? "[" + formName[cellL] + "]" : "")}->{cr}\tweld={(weld ? 1 : 0)}\tgap={gap}\t" +
                          $"cL={cellL} sp={list[cellL]} adv={advL:F1} rL={bL.r} | cR={cellR} lR={bR.l} rR={bR.r} | {(ok ? "OK" : "BAD")}");
            }
        }
        string hs = string.Join(" ", hist.Where(kv => kv.Key >= -3 && kv.Key <= 3).Select(kv => $"{kv.Key}:{kv.Value}"));
        lines.Add($"{label}\tSUMMARY\tpairs={pairs}\tbroken={broken}\tbrokenWeld={brokenWeld}\tbrokenSep={brokenSep}\t" +
                  $"weld={weldOk}/{weldN}\tminWeld={minWeld}\tminSep={(minSep == int.MaxValue ? 0 : minSep)}\tmaxSep={maxSep}\t" +
                  $"kind(arAr/mixed/latLat)={arAr}/{mixed}/{latLat}\thist={hs}");
        return (pairs, broken, lines);
    }

    static void DumpBad(string label, List<string> lines, int max)
    {
        var bad = lines.Where(s => s.StartsWith(label + "\t") && s.EndsWith("BAD")).ToList();
        if (bad.Count == 0) return;
        Console.WriteLine($"   -- {label} broken pairs ({bad.Count}, first {Math.Min(max, bad.Count)}) --");
        foreach (var b in bad.Take(max))
        {
            var f = b.Split('\t');
            if (f.Length > 1 && f[1].Length > 34) f[1] = f[1].Substring(0, 34) + "...";
            for (int i = 0; i < f.Length; i++) f[i] = f[i].Replace("\r", "").Replace("\n", "\\n");
            Console.WriteLine("      " + string.Join(" | ", f));
        }
    }

    // allocation.tsv is keyed by (letter, form) - the shaped form index is what Shape() produces
    static readonly Dictionary<(char letter, int form), int> ArabicEncCache = new();
    static bool TryArabicCell(char c, int form, out int cell)
    {
        cell = -1;
        if (ArabicEncCache.Count == 0)
            foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\allocation.tsv")).Skip(1))
            {
                var p = line.Split('\t');
                if (p.Length >= 5) ArabicEncCache[(p[0][0], int.Parse(p[2]))] = int.Parse(p[4]);
            }
        return ArabicEncCache.TryGetValue((c, form), out cell);
    }

    static int BuildEvt(int fontSize, bool extend)
    {
        string FontName = FontLabel;
        var fail = 0;
        void Check(bool ok, string msg) { Console.WriteLine($"  [{(ok ? "PASS" : "FAIL")}] {msg}"); if (!ok) fail++; }

        string modDir = ModMsgDir;
        string srcImgBar = Path.Combine(EvtSrcDir ?? modDir, "fontimage.bar");     // INSTALLED (sys already arabic)
        string srcInfBar = Path.Combine(EvtSrcDir ?? modDir, "fontinfo.bar");      // INSTALLED
        string retImgBar = Path.Combine(Root, @"technical\extracted\game-data\original\msg\us\fontimage.bar");
        string retInfBar = Path.Combine(Root, @"technical\extracted\game-data\original\msg\us\fontinfo.bar");

        COLS = E_COLS; ROWS = E_ROWS; CW = E_CW; CH = E_CH;           // activate evt geometry

        Console.WriteLine($"== buildevt: {FontName} {fontSize}px bold  extend={(extend ? "ON" : "OFF")} ==");
        Console.WriteLine($"   geometry {E_COLS}x{E_ROWS} cells of {E_CW}x{E_CH}  rgb={E_RGBLEN} list={E_LISTLEN}");

        // ---- inputs: retail evt data, and assert the installed bars still carry the same evt ----
        var rgbOrig = File.ReadAllBytes(Path.Combine(Root, @"technical\extracted\bar\us\fontimage\evt.rgb"));
        var listOrig = File.ReadAllBytes(Path.Combine(Root, @"technical\extracted\bar\us\fontinfo\evt.list"));
        Check(rgbOrig.Length == E_RGBLEN && listOrig.Length == E_LISTLEN,
            $"inputs: evt.rgb={rgbOrig.Length} evt.list={listOrig.Length} (expect {E_RGBLEN}/{E_LISTLEN})");
        if (rgbOrig.Length != E_RGBLEN || listOrig.Length != E_LISTLEN) return 1;

        var imgSrc = P.BarEntries(srcImgBar);
        var infSrc = P.BarEntries(srcInfBar);
        var imgRet = P.BarEntries(retImgBar);
        var infRet = P.BarEntries(retInfBar);
        byte[] Ent(List<(string, byte[])> l, string n) => l.First(x => x.Item1 == n).Item2;
        Check(imgSrc.Count == 3 && infSrc.Count == 4,
            $"installed bars layout: fontimage[{string.Join(",", imgSrc.Select(x => x.Item1))}] fontinfo[{string.Join(",", infSrc.Select(x => x.Item1))}]");
        Check(Ent(imgSrc, "evt").AsSpan().SequenceEqual(rgbOrig), "installed fontimage evt entry == retail evt.rgb");
        Check(Ent(imgRet, "evt").AsSpan().SequenceEqual(rgbOrig), "retail fontimage evt entry == evt.rgb");
        Check(Ent(infSrc, "evt").AsSpan().SequenceEqual(listOrig), "installed fontinfo evt entry == retail evt.list");

        // ---- tables (identical to sys build) ----
        var verdict = new Dictionary<int, string>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length < 11 || p[1] == "-") continue;
            verdict[int.Parse(p[1])] = p[10];
        }
        var alloc = new List<(char letter, int form, string formName, int cell, int code, string pf)>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\allocation.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            alloc.Add((p[0][0], int.Parse(p[2]), p[3], int.Parse(p[4]),
                Convert.ToInt32(p[5], 16), p[1]));
        }
        var baseAlloc = alloc.ToList();                                    // the 117 shapes that define baseline/metrics
        var ligRows = LamAlefOn ? LamAlefRows() : new List<(char letter, int form, string formName, int cell, int code, string pf)>();
        alloc.AddRange(ligRows);                                           // + the lam-alef ligature cell (evt only)
        var arabicCells = alloc.Select(a => a.cell).ToHashSet();
        var printable = verdict.Where(kv => kv.Value is "GLYPH" or "GLYPH-EMPTY").Select(kv => kv.Key).ToHashSet();
        var copyCells = printable.Except(arabicCells)
            .Concat(verdict.Where(kv => kv.Value == "FORBIDDEN").Select(kv => kv.Key))
            .ToList();
        Check(baseAlloc.Count == 117 && alloc.Count == 117 + ligRows.Count && arabicCells.Count == alloc.Count, $"allocation = {baseAlloc.Count} base + {ligRows.Count} lam-alef = {alloc.Count}/{arabicCells.Count} cells (expect 117 + {ligRows.Count})");
        Check(printable.Count == 214, $"printable cells = {printable.Count} (expect 214)");
        Check(copyCells.Count == 107 - ligRows.Count, $"copy cells = {copyCells.Count} (expect {107 - ligRows.Count})");
        var all = arabicCells.Concat(copyCells).ToHashSet();
        Check(all.Count == 224 && all.All(c => c >= 0 && c <= 223) && all.SetEquals(Enumerable.Range(0, 224)),
            $"arabic({arabicCells.Count}) ∪ copy({copyCells.Count}) = cells 0..223 exactly (got {all.Count}, " +
            $"outside0..223={all.Count(c => c < 0 || c > 223)})");
        Check(copyCells.All(c => !arabicCells.Contains(c)), "copy ∩ arabic = ∅");

        // punctuation redrawn in the Arabic font — retail cells are heavy/black:
        // 40='!' 41='?' 47='.' 48=',' 50=':' 51='…' 52='-' 70='-'
        var punctCells = new HashSet<int> { 40, 41, 47, 48, 50, 51, 52, 70 };
        Check(punctCells.All(copyCells.Contains) && punctCells.All(c => !arabicCells.Contains(c)),
            $"punctuation cells are retail copy cells (bad: {string.Join(",", punctCells.Where(c => !copyCells.Contains(c)))})");

        // ---- metrics pass: where does our font sit relative to the retail latin baseline ----
        using var font = MakeFont(fontSize);
        var alef = RenderGlyph(Ar.Pf['ا'][0], font, 1f);
        if (alef.bmp == null) { Console.WriteLine($"FAIL: no alef ink from {FontName} {fontSize}px"); return 1; }
        int bl = alef.b;
        alef.bmp.Dispose();
        int asc = 0, desc = 0, noInk = 0;
        foreach (var (_, _, _, _, _, pf) in baseAlloc)
        {
            var g = RenderGlyph(Convert.ToInt32(pf, 16), font, 1f);
            if (g.bmp == null) { noInk++; continue; }
            asc = Math.Max(asc, bl - g.t);
            desc = Math.Max(desc, g.b - bl);
            g.bmp.Dispose();
        }
        int baseY = Math.Min(E_RetailBaseline, E_CH - 1 - desc);
        int keepShift = E_RetailBaseline - baseY;
        int baseDelta = int.TryParse(Environment.GetEnvironmentVariable("KH2_BASE_DELTA"), out var bd) ? bd : 0;   // font-test: Arabic baseline +/-px (retail cells keep keepShift)
        baseY += baseDelta;
        bool relief = Environment.GetEnvironmentVariable("KH2_SQUEEZE_RELIEF") == "1";                            // font-test: shrink very squeezed glyphs a little instead
        float reliefMinKx = 0.6f; int reliefCount = 0;
        var reliefLog = new List<string>();
        Console.WriteLine($"   {FontName} {fontSize}px  baseline(bl)={bl}  asc={asc} desc={desc}  " +
                          $"baseY={baseY} keepShift={keepShift} (retail latin baseline {E_RetailBaseline})");
        Check(noInk == 0, $"all 117 presentation forms render ink (missing: {noInk})");
        Check(baseY >= asc, $"glyphs fit above baseline: baseY={baseY} >= asc={asc}");
        Check(baseY + desc <= E_CH - 1, $"glyphs fit below baseline: {baseY}+{desc} <= {E_CH - 1}");
        Check(keepShift >= 0 && keepShift < E_CH, $"keepShift={keepShift} within [0,{E_CH - 1}]");
        if (fail > 0) { Console.WriteLine($"RESULT: {fail} FAILURES (no output written)"); return 1; }

        // ---- buffers ----
        // start from retail so dead cells 224..335 stay byte-identical (they hold retail ink
        // in cells 224..272 that is unreachable but must not be touched), then blank the
        // 0..223 region that we fully regenerate (copy cells + arabic cells).
        var rgbNew = (byte[])rgbOrig.Clone();
        for (int cell = 0; cell < 224; cell++)
        {
            int x0 = (cell % E_COLS) * E_CW, y0 = (cell / E_COLS) * E_CH;
            for (int y = 0; y < E_CH; y++)
                for (int x = 0; x < E_CW; x++)
                    rgbNew[(y0 + y) * E_STRIDE + x0 + x] = 0;
        }
        var listNew = (byte[])listOrig.Clone();

        // 1) kept + forbidden cells: retail content moved UP by keepShift
        foreach (var cell in copyCells)
        {
            int x0 = (cell % E_COLS) * E_CW, y0 = (cell / E_COLS) * E_CH;
            for (int y = 0; y < E_CH - keepShift; y++)
                for (int x = 0; x < E_CW; x++)
                    rgbNew[(y0 + y) * E_STRIDE + x0 + x] = rgbOrig[(y0 + y + keepShift) * E_STRIDE + x0 + x];
        }

        // 2) arabic glyphs
        var glyphLog = new StringBuilder();
        glyphLog.AppendLine("letter\tpfCode\tform\tformName\tcell\tcode\tnatW\tkx\tw\ttop\tsp\textended");
        int squeezed = 0, extNone = 0, extRows = 0;
        foreach (var (letter, form, formName, cell, code, pf) in alloc)
        {
            int cp = Convert.ToInt32(pf, 16);
            // ISO/FIN do NOT join to their visual-left neighbour (jn=0), so they carry a 1px
            // left bearing; INI/MED must sit flush at x=0 because that side is the weld.
            int bearing = formName is "ISO" or "FIN" ? 1 : 0;
            int maxW = E_CW - bearing;
            var g = RenderGlyph(cp, font, 1f);
            if (g.bmp == null) { Console.WriteLine($"  FAIL no ink U+{cp:X4} {letter} form{form}"); fail++; continue; }
            int natW = g.r - g.l + 1;
            float kx = 1f;
            int w = natW;
            for (int it = 0; w > maxW && it < 6; it++)
            {
                kx *= (float)maxW / w;
                g.bmp.Dispose();
                g = RenderGlyph(cp, font, kx);
                if (g.bmp == null) break;
                w = g.r - g.l + 1;
            }
            if (g.bmp == null) { Console.WriteLine($"  FAIL squeeze U+{cp:X4}"); fail++; continue; }
            int blUse = bl;
            if (relief && kx < reliefMinKx)
            {
                float kx0 = kx; (Bitmap bmp, int l, int r, int t, int b) bestG = (null, 0, -1, 0, -1); float bestKx = kx; int bestBl = bl; float usedF = 1f;
                foreach (float f in new[] { 0.95f, 0.90f, 0.85f })
                {
                    using var fs = MakeFont(fontSize * f);
                    var al2 = RenderGlyph(Ar.Pf['ا'][0], fs, 1f); if (al2.bmp == null) continue; int bl2 = al2.b; al2.bmp.Dispose();
                    float k2 = 1f; var g2 = RenderGlyph(cp, fs, 1f); if (g2.bmp == null) continue; int w2 = g2.r - g2.l + 1;
                    for (int it = 0; w2 > maxW && it < 6; it++) { k2 *= (float)maxW / w2; g2.bmp.Dispose(); g2 = RenderGlyph(cp, fs, k2); if (g2.bmp == null) break; w2 = g2.r - g2.l + 1; }
                    if (g2.bmp == null) continue;
                    if (bestG.bmp != null) bestG.bmp.Dispose();
                    bestG = g2; bestKx = k2; bestBl = bl2; usedF = f;
                    if (k2 >= reliefMinKx) break;
                }
                if (bestG.bmp != null && bestKx > kx)
                { g.bmp.Dispose(); g = bestG; kx = bestKx; blUse = bestBl; w = g.r - g.l + 1; reliefCount++; reliefLog.Add($"{letter}\t{formName}\t{kx0:F3}\t{kx:F3}\t{usedF:F2}"); }
                else if (bestG.bmp != null) bestG.bmp.Dispose();
            }
            if (kx < 1f && !ligRows.Any(lr => lr.cell == cell)) squeezed++;
            w = Math.Min(w, maxW);
            int top = baseY + (g.t - blUse), h = g.b - g.t + 1;
            bool boundsOk = top >= 0 && top + h <= E_CH && w <= maxW;
            if (!boundsOk) { Console.WriteLine($"  FAIL bounds {letter} {formName}: w={w} top={top} h={h}"); fail++; }
            var mask = LitMask(g.bmp);
            g.bmp.Dispose();
            int blLocal = blUse - g.t;                       // baseline row inside the mask
            if (boundsOk)
            {
                int x0 = (cell % E_COLS) * E_CW, y0 = (cell / E_COLS) * E_CH;
                for (int y = 0; y < h; y++)
                    for (int x = 0; x < w; x++)
                        if (mask[y, x]) rgbNew[(y0 + top + y) * E_STRIDE + x0 + bearing + x] = Ink;

                // ---- step 3: run the joining stroke out to the cell edge on the WELDING side ----
                // welding side = right side for MED/FIN (gap after the glyph is the weld, see §3-1);
                // the left side of INI/MED already lands on x=0 by construction (we draw the cropped
                // ink box from column 0), which is what the weld pair on its left needs.
                // INI/ISO must NOT be extended on the right: that side is a separation boundary.
                if (extend && formName is "MED" or "FIN" && bearing + w < E_CW)
                {
                    int rows = 0;
                    for (int y = 0; y < h; y++)
                    {
                        if (!mask[y, 0] || !mask[y, w - 1]) continue;          // not a full-width stroke
                        if (y < blLocal - 4 || y > blLocal) continue;          // connector sits on the baseline
                        for (int x = bearing + w; x < E_CW; x++)
                            rgbNew[(y0 + top + y) * E_STRIDE + x0 + x] = Ink;
                        rows++;
                    }
                    if (rows == 0) extNone++; else extRows += rows;
                }
            }
            else fail++;
            var box = BoxOf(rgbNew, cell, E_COLS, E_CW, E_CH);
            if (box.r < 0) { fail++; continue; }
            if (box.l != bearing || box.r > E_CW - 1 || box.t < 0 || box.b > E_CH - 1)
            { Console.WriteLine($"  FAIL box {letter} {formName}: l={box.l} (want {bearing}) r={box.r} t={box.t} b={box.b}"); fail++; continue; }
            int wFinal = box.r - box.l + 1;
            int sp = 2 * wFinal + (formName is "ISO" or "INI" ? 4 + (formName == "INI" || !SepIniOnly ? SepAdj : 0) : -2);
            if (sp < 1 || sp > 255) { Console.WriteLine($"  FAIL sp {letter} {formName}: {sp}"); fail++; continue; }
            listNew[cell] = (byte)sp;
            glyphLog.AppendLine($"{letter}\t{pf}\t{form}\t{formName}\t{cell}\t{code:X2}\t{natW}\t{kx:F3}\t{wFinal}\t{box.t}\t{sp}\t{(box.r == E_CW - 1 ? 1 : 0)}");
        }
        if (relief) { Console.WriteLine($"   relief: {reliefCount} glyphs re-drawn smaller (kx<{reliefMinKx} -> better)"); foreach (var rl in reliefLog) Console.WriteLine("     relief\t" + rl); }
        Console.WriteLine($"   squeezed(kx<1)={squeezed}/117  extendedCells={117 - extNone} rows={extRows} emptyBands={extNone}");

        // 3) P3: digits keep >=1px of air from a preceding arabic glyph (§3-3, must survive rebuild)
        var digitInfo = new StringBuilder();
        for (int d = DigitCellFirst; d <= DigitCellLast; d++)
        {
            var b = BoxOf(rgbNew, d, E_COLS, E_CW, E_CH);
            int kBefore = b.r < 0 ? -999 : listOrig[d] - 2 * (b.r - b.l + 1);
            int kAfter = b.r < 0 ? -999 : listOrig[d] + DigitSpBoost - 2 * (b.r - b.l + 1);
            digitInfo.Append($" {d}:{listOrig[d]}->{listOrig[d] + DigitSpBoost}(k {kBefore}->{kAfter})");
            listNew[d] = (byte)(listOrig[d] + DigitSpBoost);
        }
        Console.WriteLine($"   digit cells{digitInfo}");

        // 4) P4: allowed punctuation redrawn in the same Arabic font/weight/baseline.
        // retail punctuation cells are heavy black outline.  The glyph is condensed to at most 75%
        // of its natural width so it fits the retail pitch; if that is still wider than the retail
        // pitch allows, the cell's own evt.list sp gets the minimal bump that restores >=1px of air
        // against a neighbour that sits at l=0 (worst case).  No other cell's sp is touched.
        var punctChar = new Dictionary<int, char>
        {
            [40] = '!', [41] = '?', [47] = '.', [48] = ',', [50] = ':', [51] = '\u2026', [52] = '-', [70] = '-',
        };
        int punctFail = 0, punctSpBump = 0;
        foreach (var cell in punctCells.OrderBy(c => c))
        {
            char ch = punctChar[cell];
            int cp = ch;
            for (int y = 0; y < E_CH; y++)
                for (int x = 0; x < E_CW; x++)
                    rgbNew[(cell / E_COLS * E_CH + y) * E_STRIDE + (cell % E_COLS) * E_CW + x] = 0;
            var g = RenderGlyph(cp, font, 1f);
            if (g.bmp == null) { Console.WriteLine($"  FAIL punct no ink U+{cp:X4} c{cell}"); punctFail++; continue; }
            int natW = g.r - g.l + 1;
            double adv = listNew[cell] / 2.0;                 // cell pitch, retail sp
            int wNeed = (int)Math.Floor(adv - 1);             // gap = adv + l_r - (r_l+1) >= 1 with l_r = 0
            int wMin = (int)Math.Ceiling(natW * 0.75);
            int target = Math.Max(wNeed, Math.Min(natW, wMin));
            if (target > E_CW) target = E_CW;
            float kx = 1f;
            int w = natW;
            for (int it = 0; w > target && it < 10; it++)
            {
                kx *= (float)target / w;
                g.bmp.Dispose();
                g = RenderGlyph(cp, font, kx);
                if (g.bmp == null) break;
                w = g.r - g.l + 1;
            }
            if (g.bmp == null) { Console.WriteLine($"  FAIL punct squeeze U+{cp:X4} c{cell}"); punctFail++; continue; }
            int top = baseY + (g.t - bl), h = g.b - g.t + 1;
            if (!(top >= 0 && top + h <= E_CH && w <= E_CW))
            {
                Console.WriteLine($"  FAIL punct bounds '{ch}' c{cell}: w={w} top={top} h={h}");
                punctFail++; g.bmp.Dispose(); continue;
            }
            var mask = LitMask(g.bmp);
            g.bmp.Dispose();
            int x0 = (cell % E_COLS) * E_CW, y0 = (cell / E_COLS) * E_CH;
            for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++)
                    if (mask[y, x]) rgbNew[(y0 + top + y) * E_STRIDE + x0 + x] = Ink;
            int spRetail = listNew[cell], spNew = spRetail;
            if (w > wNeed) { spNew = Math.Min(255, 2 * (w + 1)); listNew[cell] = (byte)spNew; }
            if (spNew != spRetail) punctSpBump++;
            var bxp = BoxOf(rgbNew, cell, E_COLS, E_CW, E_CH);
            Console.WriteLine($"   punct '{ch}' c{cell} natW={natW} kx={kx:F3} w={w} (need<={wNeed}) top={top} " +
                              $"box l={bxp.l} r={bxp.r} t={bxp.t} b={bxp.b} sp {spRetail}->{spNew}");
        }
        Check(punctFail == 0, $"all {punctCells.Count} punctuation cells redrawn in the Arabic font (failures: {punctFail})");

        // ---- ink convention: our ink must be the retail full-opacity glyph level ----
        int retailMax = 0;
        for (int i = 0; i < rgbOrig.Length; i++) if (rgbOrig[i] > retailMax) retailMax = rgbOrig[i];
        var coreH = new Dictionary<int, int>();
        for (int i = 0; i < rgbOrig.Length; i++)
        {
            byte v = rgbOrig[i];
            if (v < 33 || v > 64) continue;
            coreH[v] = coreH.TryGetValue(v, out var c) ? c + 1 : 1;
        }
        int latinMax = 0;
        foreach (var cell in new[] { 14, 15, 16 })                 // retail latin A, B, C
        {
            int x0 = (cell % E_COLS) * E_CW, y0 = (cell / E_COLS) * E_CH;
            for (int y = 0; y < E_CH; y++)
                for (int x = 0; x < E_CW; x++)
                { byte v = rgbOrig[(y0 + y) * E_STRIDE + x0 + x]; if (v > latinMax) latinMax = v; }
        }
        Console.WriteLine($"   ink: value={Ink}  retail evt.rgb max={retailMax}  latin A/B/C max={latinMax}  " +
                          $"core-band top5: " +
                          string.Join(" ", coreH.OrderByDescending(kv => kv.Value).Take(5).Select(kv => $"{kv.Key}x{kv.Value}")));
        Check(Ink == retailMax, $"SD ink = retail full-opacity level {Ink} == retail evt.rgb max {retailMax}");
        Check(Ink == latinMax, $"SD ink matches retail latin A/B/C peak {latinMax}");

        // ---- structural checks ----
        Console.WriteLine("\n== structural checks ==");
        Check(rgbNew.Length == E_RGBLEN && listNew.Length == E_LISTLEN, "output sizes rgb=131072 list=336");

        int keepBad = 0;
        foreach (var cell in copyCells.Where(c => !punctCells.Contains(c)))
        {
            int x0 = (cell % E_COLS) * E_CW, y0 = (cell / E_COLS) * E_CH;
            for (int y = 0; y < E_CH; y++)
                for (int x = 0; x < E_CW; x++)
                {
                    byte want = y < E_CH - keepShift ? rgbOrig[(y0 + y + keepShift) * E_STRIDE + x0 + x] : (byte)0;
                    if (rgbNew[(y0 + y) * E_STRIDE + x0 + x] != want) { keepBad++; goto nextCell; }
                }
            nextCell:;
        }
        Check(keepBad == 0, $"all {copyCells.Count - punctCells.Count} kept copy cells = retail shifted up {keepShift}px (punct redrawn separately; bad: {keepBad})");

        int arBad = 0, spBad = 0;
        foreach (var (_, _, formName, cell, _, _) in alloc)
        {
            var box = BoxOf(rgbNew, cell, E_COLS, E_CW, E_CH);
            int wantL = formName is "ISO" or "FIN" ? 1 : 0;
            if (box.r < 0 || box.l != wantL || box.t < 0 || box.b > E_CH - 1 || box.r > E_CW - 1) { arBad++; continue; }
            int expectSp = 2 * (box.r - box.l + 1) + (formName is "ISO" or "INI" ? 4 + (formName == "INI" || !SepIniOnly ? SepAdj : 0) : -2);
            if (listNew[cell] != expectSp) spBad++;
        }
        Check(arBad == 0, $"arabic cells ink at their bearing (l=1 for ISO/FIN, else 0) (bad: {arBad})");
        Check(spBad == 0, $"evt.list = 2*w + (ISO/INI?4:-2) for all 117 (bad: {spBad})");

        int listChanged = 0;
        for (int i = 0; i < E_LISTLEN; i++)
            if (listNew[i] != listOrig[i] && !arabicCells.Contains(i)
                && !punctCells.Contains(i)
                && (i < DigitCellFirst || i > DigitCellLast)) listChanged++;
        Check(listChanged == 0, $"evt.list unchanged outside arabic+punct+digit cells (changed: {listChanged})");

        int deadChanged = 0;
        for (int c = 224; c < E_LISTLEN; c++)
        {
            if (listNew[c] != listOrig[c]) deadChanged++;
            int x0 = (c % E_COLS) * E_CW, y0 = (c / E_COLS) * E_CH;
            for (int y = 0; y < E_CH; y++)
                for (int x = 0; x < E_CW; x++)
                    if (rgbNew[(y0 + y) * E_STRIDE + x0 + x] != rgbOrig[(y0 + y) * E_STRIDE + x0 + x]) { deadChanged++; goto nextDead; }
            nextDead:;
        }
        Check(deadChanged == 0, $"dead cells 224..335 byte-identical to retail (changed bytes/cells: {deadChanged})");

        int outGrid = 0;
        for (int y = 0; y < E_CH * E_ROWS; y++)
            for (int x = 252; x < E_STRIDE; x++)
                if (rgbNew[y * E_STRIDE + x] != rgbOrig[y * E_STRIDE + x]) outGrid++;
        for (int i = E_CH * E_ROWS * E_STRIDE; i < E_RGBLEN; i++)
            if (rgbNew[i] != rgbOrig[i]) outGrid++;
        Check(outGrid == 0, $"nothing written outside the 252x512 grid (mismatches: {outGrid})");

        int stray = 0;
        foreach (var cell in Enumerable.Range(0, 224).Except(arabicCells).Except(copyCells))
        { var b = BoxOf(rgbNew, cell, E_COLS, E_CW, E_CH); if (b.r >= 0) stray++; }
        Check(stray == 0, $"cells outside copy∪arabic are blank (stray: {stray})");

        // ---- layout simulator: zero gaps on connected pairs ----
        Console.WriteLine("\n== layout simulator (gap = sp/2 + l_right - (r_left+1), SD px) ==");
        var formNameMap = alloc.ToDictionary(a => a.cell, a => a.formName);
        var charCell = LoadCharCell();
        var words = LoadWords(@"translation\batchtt1.tsv", @"translation\batch1.tsv")
            .Concat(new[] { "حلمت به مرة أخرى...", "ماذا عن سايفر?", "لنستكشف الأمر!" }).Distinct().ToList();
        var (pairs, broken, gapLines) = GapTable("evt", rgbNew, listNew, E_COLS, E_CW, E_CH, formNameMap, charCell, words);
        var summary = gapLines.Last();
        var minWeld = int.Parse(summary.Split('\t').First(s => s.StartsWith("minWeld=")).Substring(8));
        var maxSep = int.Parse(summary.Split('\t').First(s => s.StartsWith("maxSep=")).Substring(7));
        Check(broken == 0, $"evt: {pairs} pairs, broken={broken}  ({summary})");
        DumpBad("evt", gapLines, 25);
        Check(minWeld <= 0, $"connected pairs touch/overlap: minWeld={minWeld} (must be <= 0)");
        Check(maxSep >= 1, $"separated pairs keep air: maxSep={maxSep} (must be >= 1)");

        // calibration: same simulator on the installed sys atlas must reproduce joinfix (0 broken)
        var sysRgb = File.ReadAllBytes(Path.Combine(Root, @"font-rtl\arabic\out\sys.rgb"));
        var sysList = P.BarEntries(Path.Combine(modDir, "fontinfo.bar")).First(x => x.Item1 == "sys").Item2;
        var sysWords = LoadWords(@"translation\batch1.tsv");
        if (sysRgb.Length == 65536 && sysList.Length == 280 && sysWords.Count > 0)
        {
            var (sp2, br2, ln2) = GapTable("sys", sysRgb, sysList, 28, 9, 24, formNameMap, charCell, sysWords);
            Check(br2 == 0, $"calibration on installed sys atlas: {sp2} pairs broken={br2} (joinfix reported 0)");
            DumpBad("sys", ln2, 25);
            gapLines.AddRange(ln2);
        }

        // ---- write outputs ----
        if (fail > 0)
        {
            Console.WriteLine($"RESULT: {fail} FAILURES (nothing written)");
            return 1;
        }
        var outDir = EvtOut;
        Directory.CreateDirectory(outDir);
        File.WriteAllBytes(Path.Combine(outDir, "evt.rgb"), rgbNew);
        File.WriteAllBytes(Path.Combine(outDir, "evt.list"), listNew);
        File.WriteAllText(Path.Combine(outDir, "build_glyphs_evt.tsv"), glyphLog.ToString(), new UTF8Encoding(false));
        File.WriteAllLines(Path.Combine(outDir, "gaps.tsv"), gapLines);

        P.BarReplace(srcImgBar, Path.Combine(outDir, "fontimage.bar"), "evt", rgbNew);
        P.BarReplace(srcInfBar, Path.Combine(outDir, "fontinfo.bar"), "evt", listNew);

        Console.WriteLine("\n== bar repack checks (source = INSTALLED bars, only evt differs) ==");
        var imgDst = P.BarEntries(Path.Combine(outDir, "fontimage.bar"));
        var infDst = P.BarEntries(Path.Combine(outDir, "fontinfo.bar"));
        bool EntriesOk(List<(string, byte[])> src, List<(string, byte[])> dst, string name, byte[] data)
        {
            if (src.Count != dst.Count) return false;
            for (int i = 0; i < src.Count; i++)
            {
                if (src[i].Item1 != dst[i].Item1) return false;
                var want = dst[i].Item1 == name ? data : src[i].Item2;
                if (!dst[i].Item2.AsSpan().SequenceEqual(want.AsSpan())) return false;
            }
            return true;
        }
        Check(EntriesOk(imgSrc, imgDst, "evt", rgbNew),
            $"fontimage.bar: evt replaced, sys+icon byte-identical to INSTALLED [{string.Join(",", imgDst.Select(x => x.Item1))}]");
        Check(EntriesOk(infSrc, infDst, "evt", listNew),
            $"fontinfo.bar: evt replaced, sys+icon+md_m byte-identical to INSTALLED [{string.Join(",", infDst.Select(x => x.Item1))}]");
        foreach (var name in new[] { "sys", "icon" })
            Check(Ent(imgDst, name).AsSpan().SequenceEqual(Ent(imgSrc, name)), $"fontimage '{name}' byte-identical to installed");
        foreach (var name in new[] { "sys", "icon", "md_m" })
            Check(Ent(infDst, name).AsSpan().SequenceEqual(Ent(infSrc, name)), $"fontinfo '{name}' byte-identical to installed");

        // ---- report ----
        var rep = new StringBuilder();
        rep.AppendLine($"buildevt: {FontName} {fontSize}px bold  extend={(extend ? "ON" : "OFF")}");
        rep.AppendLine($"geometry: {E_COLS}x{E_ROWS} cells {E_CW}x{E_CH}  rgb={E_RGBLEN} list={E_LISTLEN} stride={E_STRIDE}");
        rep.AppendLine($"metrics : baseline(bl)={bl} asc={asc} desc={desc} baseY={baseY} keepShift={keepShift} retailLatinBaseline={E_RetailBaseline}");
        rep.AppendLine($"inputs  : evt.rgb sha256={Sha256Str(rgbOrig)}  evt.list sha256={Sha256Str(listOrig)}");
        rep.AppendLine($"         fontimage.bar(installed) sha256={Sha256Str(File.ReadAllBytes(srcImgBar))}");
        rep.AppendLine($"         fontinfo.bar(installed)  sha256={Sha256Str(File.ReadAllBytes(srcInfBar))}");
        rep.AppendLine($"outputs : evt.rgb sha256={Sha256Str(rgbNew)}");
        rep.AppendLine($"         evt.list sha256={Sha256Str(listNew)}");
        foreach (var f in new[] { "evt.rgb", "evt.list", "fontimage.bar", "fontinfo.bar" })
        {
            var b = File.ReadAllBytes(Path.Combine(outDir, f));
            rep.AppendLine($"         {f} sha256={Sha256Str(b)} size={b.Length}");
        }
        rep.AppendLine($"gaps    : {summary}");
        rep.AppendLine($"checks  : fail={fail}");
        rep.AppendLine($"RESULT: {(fail == 0 ? "ALL PASS" : fail + " FAILURES")}");
        File.WriteAllText(Path.Combine(outDir, "BUILD_REPORT_EVT.txt"), rep.ToString());

        Console.WriteLine($"\nwrote {outDir}");
        Console.WriteLine($"RESULT: {(fail == 0 ? "ALL PASS" : fail + " FAILURES")}");
        return fail == 0 ? 0 : 1;
    }

    /// Pen-layout pass in ATLAS texel coords. Mirrors ComposeVisual but records each drawn
    /// piece (kind/cell/x/y) so the HD compositor can replay it at 4x/2x scale.
    /// x already includes the ISO/FIN left bearing (the game blits the whole cell at pen).
    static (List<(bool isAr, int cell, float x, int y, Bitmap bmp)> items, float endPen) BuildCompose(
        List<(char c, int form, bool jp)> vis, byte[] rgb, byte[] spacing,
        Dictionary<char, int> charCell,
        Dictionary<(char, int), (Bitmap bmp, int t, int w, int l)> glyphs,
        Dictionary<(char, int), int> glyphCell,
        int baseY, int bl, float startX)
    {
        var items = new List<(bool, int, float, int, Bitmap)>();
        float pen = startX;
        foreach (var (c, form, jp) in vis)
        {
            if (form >= 0 && glyphs.TryGetValue((c, form), out var g) && g.bmp != null)
            {
                items.Add((true, glyphCell.TryGetValue((c, form), out var gc) ? gc : -1, pen + g.l, g.t, g.bmp));
                pen += g.w + (jp ? -1 : 2);
            }
            else if (c == ' ') pen += 5;
            else if (charCell.TryGetValue(c, out var cell))
            {
                items.Add((false, cell, pen, 0, null));
                pen += spacing[cell] / 2f;
            }
            else pen += 5;
        }
        return (items, pen);
    }

    /// Blit a BuildCompose layout into a strip of E_CW x E_CH atlas cells (SD texels, keepShift=0).
    static void BlitCompose(List<(bool isAr, int cell, float x, int y, Bitmap bmp)> items, Bitmap target,
        byte[] rgb)
    {
        using var g = Graphics.FromImage(target);
        foreach (var (isAr, cell, x, y, bmp) in items)
        {
            int px = (int)Math.Round(x);
            if (isAr) { g.DrawImage(bmp, px, y); continue; }
            int x0 = (cell % E_COLS) * E_CW, y0 = (cell / E_COLS) * E_CH;
            for (int yy = 0; yy < E_CH; yy++)
                for (int xx = 0; xx < E_CW; xx++)
                {
                    int tx = px + xx;
                    if (tx < 0 || tx >= target.Width) continue;
                    if (rgb[(y0 + yy) * E_STRIDE + x0 + xx] != 0) target.SetPixel(tx, yy, Color.White);
                }
        }
    }

    /// Render the three review phrases from the BUILT evt atlas at the game's own texel scale.
    static int PreviewEvt(int fontSize)
    {
        var fail = 0;
        void Check(bool ok, string msg) { Console.WriteLine($"  [{(ok ? "PASS" : "FAIL")}] {msg}"); if (!ok) fail++; }

        COLS = E_COLS; ROWS = E_ROWS; CW = E_CW; CH = E_CH;
        var outDir = Path.Combine(Root, @"font-rtl\arabic\out\evt");
        string rgbPath = Path.Combine(outDir, "evt.rgb");
        if (!File.Exists(rgbPath)) { Console.WriteLine("FAIL: run buildevt first"); return 1; }
        var rgb = File.ReadAllBytes(rgbPath);
        var list = File.ReadAllBytes(Path.Combine(outDir, "evt.list"));
        Check(rgb.Length == E_RGBLEN && list.Length == E_LISTLEN, $"inputs evt.rgb={rgb.Length} evt.list={list.Length}");

        var formNameMap = LoadFormNames();
        var charCell = LoadCharCell();
        var glyphs = new Dictionary<(char, int), (Bitmap bmp, int t, int w, int l)>();
        var glyphCell = new Dictionary<(char, int), int>();
        foreach (var (letter, form, formName, cell, _, _) in LoadAllocRows())
        {
            var box = BoxOf(rgb, cell, E_COLS, E_CW, E_CH);
            if (box.r < 0) continue;
            int w = box.r - box.l + 1, h = box.b - box.t + 1;
            var bmp = new Bitmap(w, h, PixelFormat.Format32bppArgb);
            int x0 = (cell % E_COLS) * E_CW, y0 = (cell / E_COLS) * E_CH;
            for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++)
                    if (rgb[(y0 + box.t + y) * E_STRIDE + x0 + box.l + x] != 0)
                        bmp.SetPixel(x, y, Color.White);
            glyphs[(letter, form)] = (bmp, box.t, w, box.l);
            glyphCell[(letter, form)] = cell;
        }
        Check(glyphs.Count == 117, $"glyphs extracted from built evt atlas: {glyphs.Count}/117");

        string[] phrases = { "حلمت به مرة أخرى...", "ماذا عن سايفر?", "لنستكشف الأمر!" };
        // recompute baseY exactly like the build did
        using var font = new Font("Segoe UI", fontSize, FontStyle.Bold, GraphicsUnit.Pixel);
        var alef = RenderGlyph(Ar.Pf['ا'][0], font, 1f);
        int bl = alef.b; alef.bmp.Dispose();
        int desc = 0;
        foreach (var (_, _, _, _, _, pf) in LoadAllocRows())
        {
            var g = RenderGlyph(Convert.ToInt32(pf, 16), font, 1f);
            if (g.bmp == null) continue;
            desc = Math.Max(desc, g.b - bl);
            g.bmp.Dispose();
        }
        int baseY = Math.Min(E_RetailBaseline, E_CH - 1 - desc);
        Console.WriteLine($"   preview baseY={baseY} (recomputed)  scale: HD texel = SD px * 4 wide / * 2 tall");

        using var small = new Font("Arial", 9f);
        int lineH = E_CH + 44;
        var img = new Bitmap(1400, lineH * (phrases.Length * 2) + 40, PixelFormat.Format32bppArgb);
        using (var g = Graphics.FromImage(img))
        {
            g.Clear(Color.FromArgb(16, 16, 20));
            g.DrawString($"evt atlas preview — {fontSize}px — baseline y={baseY} — texel = atlas pixel (1:1)", small,
                Brushes.Yellow, 8, 6);
            int y = 26;
            using var layout = new StreamWriter(Path.Combine(outDir, "hd_layout.tsv"), false, new UTF8Encoding(false));
            layout.WriteLine("phrase\ttext\tseq\tkind\tcell\tx");
            int phraseIdx = 0;
            foreach (var phrase in phrases)
            {
                var (items, endPen) = BuildCompose(ToVisual(Shape(phrase)), rgb, list, charCell, glyphs, glyphCell, bl, bl, 12);
                Console.WriteLine($"   visual L->R: {string.Join(" ", ToVisual(Shape(phrase)).Select(v => v.form >= 0 ? $"AR{((int)v.c):X4}" : v.c == ' ' ? "SP" : $"SC{(int)v.c:X2}"))}");
                int seq = 0;
                foreach (var it in items)
                    layout.WriteLine($"{phraseIdx}\t{phrase}\t{seq++}\t{(it.isAr ? "A" : "L")}\t{it.cell}\t{it.x:F2}");
                phraseIdx++;
                for (int pass = 0; pass < 2; pass++)
                {
                    int scale = pass == 0 ? 1 : 2;
                    int startX = 12;
                    var strip = new Bitmap(1300, E_CH, PixelFormat.Format32bppArgb);
                    BlitCompose(items, strip, rgb);
                    float end = endPen;
                    g.DrawString($"{(pass == 0 ? "1:1 texel" : "x2")}  {phrase}   endPen={end:F0}", small,
                        pass == 0 ? Brushes.Lime : Brushes.Orange, 8, y);
                    y += 14;
                    var crop = Crop(strip, (int)end + 8);
                    if (scale > 1)
                    {
                        var up = new Bitmap(crop.Width * scale, crop.Height * scale, PixelFormat.Format32bppArgb);
                        using var g2 = Graphics.FromImage(up);
                        g2.InterpolationMode = InterpolationMode.NearestNeighbor;
                        g2.PixelOffsetMode = PixelOffsetMode.Half;
                        g2.DrawImage(crop, 0, 0, up.Width, up.Height);
                        crop.Dispose();
                        crop = up;
                    }
                    g.DrawImage(crop, startX, y);
                    y += E_CH * scale + 8;
                }
                y += 8;
            }
        }
        string path = Path.Combine(outDir, $"preview_evt_{fontSize}.png");
        img.Save(path, ImageFormat.Png);
        img.Dispose();
        Check(File.Exists(path), $"preview written: {path} ({new FileInfo(path).Length} bytes)");
        Console.WriteLine($"RESULT: {(fail == 0 ? "ALL PASS" : fail + " FAILURES")}");
        return fail == 0 ? 0 : 1;
    }

    static List<(char letter, int form, string formName, int cell, int code, string pf)> LoadAllocRows()
    {
        var alloc = new List<(char, int, string, int, int, string)>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\allocation.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            alloc.Add((p[0][0], int.Parse(p[2]), p[3], int.Parse(p[4]),
                Convert.ToInt32(p[5], 16), p[1]));
        }
        return alloc;
    }

    // ================= cell allocation: sacrifice pool -> Arabic (letter,form) cells =================
    static int Alloc()
    {
        // --- load codemap ---
        var cellInfo = new Dictionary<int, (int code, string kind, string ch, long text, string verdict)>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length < 11) continue;
            if (p[1] == "-") continue;
            int cell = int.Parse(p[1]);
            cellInfo[cell] = (Convert.ToInt32(p[0], 16), p[4], p[5], long.TryParse(p[7], out var t) ? t : 0, p[10]);
        }

        // --- tier pools exactly per PROJECT_STATE §4-6-8 (row-table of §4-6-5) ---
        static IEnumerable<int> Range(int a, int b) { for (int i = a; i <= b; i++) yield return i; }
        var t1 = new[] { 95, 96, 97, 98, 99, 102, 103, 104, 105, 106, 108 }
            .Concat(Range(148, 167)).Concat(Range(168, 171)).Concat(Range(176, 195))
            .Concat(Range(196, 203)).Concat(new[] { 212 }).Concat(Range(214, 222)).ToList();
        var t2 = Range(122, 147).ToList();   // a-z
        var t3 = Range(14, 39).ToList();     // A-Z
        var pool = t1.Select(c => (c, 1)).Concat(t2.Select(c => (c, 2))).Concat(t3.Select(c => (c, 3))).ToList();

        // --- validations ---
        int fail = 0;
        void Check(bool ok, string msg) { Console.WriteLine($"  [{(ok ? "PASS" : "FAIL")}] {msg}"); if (!ok) fail++; }
        Check(t1.Count == 73 && t2.Count == 26 && t3.Count == 26 && pool.Count == 125,
            $"tier sizes T1={t1.Count} T2={t2.Count} T3={t3.Count} total={pool.Count} (expect 73/26/26/125)");
        var forbiddenCells = cellInfo.Where(kv => kv.Value.verdict == "FORBIDDEN").Select(kv => kv.Key).ToHashSet();
        var poolCells = pool.Select(x => x.c).ToHashSet();
        Check(!poolCells.Overlaps(forbiddenCells),
            $"pool ∩ FORBIDDEN = {string.Join(",", poolCells.Intersect(forbiddenCells))} (expect empty)");
        var nonGlyph = poolCells.Where(c => !cellInfo.ContainsKey(c) || cellInfo[c].verdict is not ("GLYPH" or "GLYPH-EMPTY")).ToList();
        Check(nonGlyph.Count == 0, $"pool cells all GLYPH (bad: {string.Join(",", nonGlyph)})");

        // --- needed Arabic glyphs, deterministic order (letter ordinal, then form) ---
        var needed = Ar.Needed()
            .OrderBy(x => x.letter).ThenBy(x => x.form).ToList();
        Check(needed.Count == 117, $"needed glyphs = {needed.Count} (expect 117)");

        // --- pool order: (tier, textCount asc, cell asc); take first N ---
        var ordered = pool
            .OrderBy(x => x.Item2)
            .ThenBy(x => cellInfo[x.c].text)
            .ThenBy(x => x.c)
            .ToList();
        bool fits = needed.Count <= ordered.Count;
        Check(fits, $"needed {needed.Count} <= pool {ordered.Count} (spare {ordered.Count - needed.Count})");
        if (!fits) { Console.WriteLine("  ALLOCATION IMPOSSIBLE"); return 1; }

        var take = ordered.Take(needed.Count).ToList();
        var spare = ordered.Skip(needed.Count).ToList();

        // --- emit allocation.tsv ---
        var sb = new StringBuilder();
        sb.AppendLine("letter\tpfCode\tform\tformName\tcell\tcode\tsacChar\tsacCode\tsacTextCount\ttier");
        var formName = new[] { "ISO", "FIN", "INI", "MED" };
        for (int i = 0; i < needed.Count; i++)
        {
            var (letter, form) = needed[i];
            var (cell, tier) = take[i];
            var info = cellInfo[cell];
            sb.AppendLine(string.Join("\t",
                letter, $"{Ar.Pf[letter][form]:X4}", form, formName[form],
                cell, $"{info.code:X2}", info.ch, $"{info.code:X2}", info.text, tier));
        }
        var outTsv = Path.Combine(Root, @"font-rtl\arabic\allocation.tsv");
        File.WriteAllText(outTsv, sb.ToString(), new UTF8Encoding(false));
        Console.WriteLine($"wrote {outTsv}");

        // --- report ---
        Console.WriteLine($"\n== allocation: {take.Count} cells taken from pool {ordered.Count}, spare {spare.Count} ==");
        Console.WriteLine($"spare cells (kept original Latin): {string.Join(" ", spare.Select(x => $"'{cellInfo[x.c].ch}'({cellInfo[x.c].text})"))}");
        var forbiddenCodes = cellInfo.Where(kv => kv.Value.verdict == "FORBIDDEN").Select(kv => kv.Value.code).ToHashSet();
        var badCodes = take.Where(x => forbiddenCodes.Contains(cellInfo[x.c].code)).ToList();
        Check(badCodes.Count == 0, $"allocated codes ∉ FORBIDDEN codes");
        var dupCells = take.Select(x => x.c).GroupBy(c => c).Where(g => g.Count() > 1).ToList();
        Check(dupCells.Count == 0, $"no duplicate cells assigned");
        var tierUse = take.GroupBy(x => x.Item2).OrderBy(g => g.Key)
            .Select(g => $"T{g.Key}={g.Count()}");
        Console.WriteLine($"tier usage: {string.Join(" ", tierUse)}  (T1 pool 73, T2 pool 26, T3 pool 26)");
        Console.WriteLine($"\nRESULT: {(fail == 0 ? "ALL PASS" : fail + " FAILURES")}");
        return fail == 0 ? 0 : 1;
    }

    // ================= build: render final sys.rgb/sys.list + repack bars =================
    static string Sha256Str(byte[] data) =>
        Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();

    /// <summary>Binary lit-mask (R>60) of a bitmap via LockBits.</summary>
    static bool[,] LitMask(Bitmap bmp)
    {
        var bd = bmp.LockBits(new Rectangle(0, 0, bmp.Width, bmp.Height),
            ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
        try
        {
            int W = bmp.Width, H = bmp.Height;
            var buf = new byte[Math.Abs(bd.Stride) * H];
            Marshal.Copy(bd.Scan0, buf, 0, buf.Length);
            var m = new bool[H, W];
            for (int y = 0; y < H; y++)
                for (int x = 0; x < W; x++)
                    m[y, x] = buf[y * bd.Stride + x * 4 + 2] > 60;
            return m;
        }
        finally { bmp.UnlockBits(bd); }
    }

    /// <summary>Extract built cell as white bitmap + cell-local ink box (l always 0).</summary>
    static (Bitmap bmp, int l, int r, int t, int b) ExtractCellGlyph(byte[] rgb, int cell)
    {
        var box = CellBox(rgb, cell);
        if (box.r < 0) return (null, 0, -1, 0, -1);
        int w = box.r - box.l + 1, h = box.b - box.t + 1;
        var bmp = new Bitmap(w, h, PixelFormat.Format32bppArgb);
        int x0 = (cell % COLS) * CW, y0 = (cell / COLS) * CH;
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                if (rgb[(y0 + box.t + y) * 256 + x0 + box.l + x] != 0)
                    bmp.SetPixel(x, y, Color.White);
        return (bmp, box.l, box.r, box.t, box.b);
    }

    static int Build()
    {
        const string FontName = "Segoe UI";
        const int FontSize = 16, BaseY = 18, KeepShift = 2;
        const string FontImageBar = @"technical\extracted\game-data\original\msg\us\fontimage.bar";
        const string FontInfoBar = @"technical\extracted\game-data\original\msg\us\fontinfo.bar";

        var rgbOrig = File.ReadAllBytes(Path.Combine(Root, @"technical\extracted\bar\us\fontimage\sys.rgb"));
        var listOrig = File.ReadAllBytes(Path.Combine(Root, @"technical\extracted\bar\us\fontinfo\sys.list"));
        if (rgbOrig.Length != 65536 || listOrig.Length != 280)
        { Console.WriteLine($"FAIL input sizes rgb={rgbOrig.Length} list={listOrig.Length}"); return 1; }

        int fail = 0;
        void Check(bool ok, string msg) { Console.WriteLine($"  [{(ok ? "PASS" : "FAIL")}] {msg}"); if (!ok) fail++; }

        // --- verdicts from codemap; cells to copy (all printable keep + forbidden, shifted) ---
        var verdict = new Dictionary<int, string>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length < 11 || p[1] == "-") continue;
            verdict[int.Parse(p[1])] = p[10];
        }
        // --- allocation ---
        var alloc = new List<(char letter, int form, string formName, int cell, int code, string pf)>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\allocation.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            alloc.Add((p[0][0], int.Parse(p[2]), p[3], int.Parse(p[4]),
                Convert.ToInt32(p[5], 16), p[1]));
        }
        var arabicCells = alloc.Select(a => a.cell).ToHashSet();
        var printable = verdict.Where(kv => kv.Value is "GLYPH" or "GLYPH-EMPTY").Select(kv => kv.Key).ToHashSet();
        var copyCells = printable.Except(arabicCells)
            .Concat(verdict.Where(kv => kv.Value == "FORBIDDEN").Select(kv => kv.Key))
            .ToList();
        Check(alloc.Count == 117 && arabicCells.Count == 117, $"allocation = {alloc.Count} rows / {arabicCells.Count} unique cells (expect 117)");
        Check(printable.Count == 214, $"printable cells = {printable.Count} (expect 214)");
        Check(copyCells.Count == 107, $"copy cells (97 kept + 10 forbidden) = {copyCells.Count} (expect 107)");
        Check(!arabicCells.Overlaps(printable.Except(arabicCells).ToHashSet()) && arabicCells.IsSubsetOf(printable),
            "arabic cells are a subset of printable");
        Check(!arabicCells.Overlaps(verdict.Where(kv => kv.Value == "FORBIDDEN").Select(kv => kv.Key)),
            "arabic cells ∩ FORBIDDEN = ∅");

        // --- new buffers ---
        var rgbNew = new byte[65536];
        var listNew = (byte[])listOrig.Clone();

        // 1) copy kept + forbidden cells with vertical shift -2
        foreach (var cell in copyCells)
        {
            int x0 = (cell % COLS) * CW, y0 = (cell / COLS) * CH;
            for (int y = 0; y < CH - KeepShift; y++)
                for (int x = 0; x < CW; x++)
                    rgbNew[(y0 + y) * 256 + x0 + x] = rgbOrig[(y0 + y + KeepShift) * 256 + x0 + x];
        }

        // 2) render Arabic glyphs into their cells
        var glyphLog = new StringBuilder();
        glyphLog.AppendLine("letter\tpfCode\tform\tformName\tcell\tcode\tnatW\tkx\tw\ttop\tsp");
        using var font = new Font(FontName, FontSize, FontStyle.Bold, GraphicsUnit.Pixel);
        var alef = RenderGlyph(Ar.Pf['ا'][0], font, 1f);
        if (alef.bmp == null) { Console.WriteLine("FAIL: no alef ink from " + FontName); return 1; }
        int bl = alef.b;
        alef.bmp.Dispose();
        Console.WriteLine($"font={FontName} {FontSize}px  baseline(bl)={bl}  drawn baseline={BaseY}  keepShift={KeepShift}");

        foreach (var (letter, form, formName, cell, code, pf) in alloc)
        {
            int cp = Convert.ToInt32(pf, 16);
            var g = RenderGlyph(cp, font, 1f);
            if (g.bmp == null) { Console.WriteLine($"  FAIL no ink U+{cp:X4} {letter} form{form}"); fail++; continue; }
            int natW = g.r - g.l + 1;
            float kx = 1f;
            int w = natW;
            // iterative squeeze: grid-fit can round back up, so loop until <= CW
            for (int it = 0; w > CW && it < 5; it++)
            {
                kx *= (float)CW / w;
                g.bmp.Dispose();
                g = RenderGlyph(cp, font, kx);
                if (g.bmp == null) break;
                w = g.r - g.l + 1;
            }
            if (g.bmp == null) { Console.WriteLine($"  FAIL squeeze render U+{cp:X4} {letter}"); fail++; continue; }
            w = Math.Min(w, CW); // clip fallback (draws only first CW columns)
            int top = BaseY + (g.t - bl), h = g.b - g.t + 1;
            bool boundsOk = top >= 0 && top + h <= CH;
            if (!boundsOk) Console.WriteLine($"  FAIL bounds {letter} form{form}: w={w} top={top} h={h}");
            var mask = LitMask(g.bmp);
            g.bmp.Dispose();
            if (boundsOk)
            {
                int x0 = (cell % COLS) * CW, y0 = (cell / COLS) * CH;
                for (int y = 0; y < h; y++)
                    for (int x = 0; x < w; x++)
                        if (mask[y, x]) rgbNew[(y0 + top + y) * 256 + x0 + x] = Ink;
            }
            else fail++;
            int sp = 2 * w + (formName is "ISO" or "INI" ? 4 : -2);
            if (sp < 1 || sp > 255) { Console.WriteLine($"  FAIL sp out of range {letter} {formName}: w={w} sp={sp}"); fail++; }
            listNew[cell] = (byte)sp;
            glyphLog.AppendLine($"{letter}\t{pf}\t{form}\t{formName}\t{cell}\t{code:X2}\t{natW}\t{kx:F3}\t{w}\t{top}\t{sp}");
        }
        File.WriteAllText(Path.Combine(Root, @"font-rtl\arabic\build_glyphs.tsv"),
            glyphLog.ToString(), new UTF8Encoding(false));

        // 2b) P3: boost digit spacing so a number keeps >=1px from a preceding Arabic
        //     glyph (reason at DigitCellFirst declaration; see PROJECT_STATE section P3).
        for (int d = DigitCellFirst; d <= DigitCellLast; d++)
            listNew[d] = (byte)(listOrig[d] + DigitSpBoost);

        // 3) structural verifications
        Console.WriteLine("\n== structural checks ==");
        Check(rgbNew.Length == 65536 && listNew.Length == 280, "output sizes: rgb=65536 list=280");

        int keepBad = 0;
        foreach (var cell in copyCells)
        {
            int x0 = (cell % COLS) * CW, y0 = (cell / COLS) * CH;
            for (int y = 0; y < CH; y++)
                for (int x = 0; x < CW; x++)
                {
                    byte want = y < CH - KeepShift ? rgbOrig[(y0 + y + KeepShift) * 256 + x0 + x] : (byte)0;
                    if (rgbNew[(y0 + y) * 256 + x0 + x] != want) { keepBad++; goto nextCell; }
                }
            nextCell:;
        }
        Check(keepBad == 0, $"all {copyCells.Count} copied cells are byte-exact orig[y+2] (bad cells: {keepBad})");

        int arBad = 0, arLeft = 0, spBad = 0;
        foreach (var (letter, form, formName, cell, code, pf) in alloc)
        {
            var box = CellBox(rgbNew, cell);
            if (box.r < 0 || box.l != 0 || box.t < 0 || box.b > CH - 1 || box.r > CW - 1) { arBad++; continue; }
            if (box.l != 0) arLeft++;
            int expectSp = 2 * (box.r - box.l + 1) + (formName is "ISO" or "INI" ? 4 : -2);
            if (listNew[cell] != expectSp) spBad++;
        }
        Check(arBad == 0, $"arabic cells ink within cell bounds (bad: {arBad})");
        Check(spBad == 0, $"sys.list sp = 2*w + (ISO/INI?4:-2) for all 117 (bad: {spBad})");

        int listChanged = 0;
        for (int i = 0; i < 280; i++)
            if (listNew[i] != listOrig[i] && !arabicCells.Contains(i)
                && (i < DigitCellFirst || i > DigitCellLast)) listChanged++;
        Check(listChanged == 0, $"sys.list unchanged outside arabic+digit cells (changed: {listChanged})");

        int digitBad = 0;
        for (int d = DigitCellFirst; d <= DigitCellLast; d++)
            if (listNew[d] != (byte)(listOrig[d] + DigitSpBoost)) digitBad++;
        Check(digitBad == 0, $"digit cells {DigitCellFirst}-{DigitCellLast} = original + {DigitSpBoost} (bad: {digitBad})");

        int strayInk = 0;
        var accounted = arabicCells.Concat(copyCells).ToHashSet();
        for (int cell = 0; cell < COLS * ROWS; cell++)
        {
            if (accounted.Contains(cell)) continue;
            var box = CellBox(rgbNew, cell);
            if (box.r >= 0) strayInk++;
        }
        Check(strayInk == 0, $"cells outside copy∪arabic are blank (stray: {strayInk})");
        for (int cell = COLS * ROWS; cell < 280; cell++)
        {
            var box = CellBox(rgbNew, cell);
            if (box.r >= 0) { strayInk++; }
        }
        Check(strayInk == 0, $"dead rows 8-9 (cells 224-279) blank (stray: {strayInk})");

        // 4) write outputs only if all checks passed
        var outDir = Path.Combine(Root, @"font-rtl\arabic\out");
        var report = new StringBuilder();
        report.AppendLine($"build: {FontName} {FontSize}px baseY={BaseY} keepShift={KeepShift} ink=0x32");
        report.AppendLine($"inputs:  sys.rgb={Sha256Str(rgbOrig)}  sys.list={Sha256Str(listOrig)}");
        report.AppendLine($"checks:  fail={fail}");
        if (fail == 0)
        {
            Directory.CreateDirectory(outDir);
            File.WriteAllBytes(Path.Combine(outDir, "sys.rgb"), rgbNew);
            File.WriteAllBytes(Path.Combine(outDir, "sys.list"), listNew);
            P.BarReplace(Path.Combine(Root, FontImageBar), Path.Combine(outDir, "fontimage.bar"), "sys", rgbNew);
            P.BarReplace(Path.Combine(Root, FontInfoBar), Path.Combine(outDir, "fontinfo.bar"), "sys", listNew);

            // verify repacked bars: other entries byte-identical, sys = new data
            var imgSrc = P.BarEntries(Path.Combine(Root, FontImageBar));
            var imgDst = P.BarEntries(Path.Combine(outDir, "fontimage.bar"));
            var infSrc = P.BarEntries(Path.Combine(Root, FontInfoBar));
            var infDst = P.BarEntries(Path.Combine(outDir, "fontinfo.bar"));
            bool EntriesOk(List<(string, byte[])> src, List<(string, byte[])> dst, string sysName, byte[] sysData)
            {
                if (src.Count != dst.Count) return false;
                for (int i = 0; i < src.Count; i++)
                {
                    if (src[i].Item1 != dst[i].Item1) return false;
                    var want = dst[i].Item1 == sysName ? sysData : src[i].Item2;
                    if (!dst[i].Item2.AsSpan().SequenceEqual(want.AsSpan())) return false;
                }
                return true;
            }
            Console.WriteLine("\n== bar repack checks ==");
            bool imgOk = EntriesOk(imgSrc, imgDst, "sys", rgbNew);
            bool infOk = EntriesOk(infSrc, infDst, "sys", listNew);
            Check(imgOk, $"fontimage.bar: sys replaced, evt+icon byte-identical (entries {string.Join(",", dst0())})");
            Check(infOk, "fontinfo.bar: sys replaced, evt+icon+md_m byte-identical");
            string[] dst0() => imgDst.Select(x => x.Item1).ToArray();

            report.AppendLine($"outputs: sys.rgb={Sha256Str(rgbNew)}");
            report.AppendLine($"         sys.list={Sha256Str(listNew)}");
            foreach (var f in new[] { "sys.rgb", "sys.list", "fontimage.bar", "fontinfo.bar" })
            {
                var b = File.ReadAllBytes(Path.Combine(outDir, f));
                report.AppendLine($"         {f} sha256={Sha256Str(b)} size={b.Length}");
            }

            // 5) end-to-end visual verification from the BUILT atlas
            var charCell = new Dictionary<char, int>();
            foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
            {
                var p = line.Split('\t');
                if (p.Length < 11 || p[10] != "GLYPH" || p[5].Length != 1) continue;
                int cell = int.Parse(p[1]);
                if (cell >= 0) charCell[p[5][0]] = cell;
            }
            var glyphs = new Dictionary<(char, int), (Bitmap bmp, int t, int w)>();
            foreach (var (letter, form, _, cell, _, _) in alloc)
            {
                var (bmp, l, r, t, b) = ExtractCellGlyph(rgbNew, cell);
                if (bmp != null) glyphs[(letter, form)] = (bmp, t, r - l + 1);
            }
            Console.WriteLine($"glyphs extracted from built atlas: {glyphs.Count}/117");
            const string Phrase = "السلام عليكم 123";
            const string Alpha = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي";
            var visDiag = ToVisual(Shape(Phrase));
            Console.WriteLine("phrase items: " + string.Join(" | ", visDiag.Select(x =>
                x.form >= 0
                    ? $"{x.c}/f{x.form}/jp{(x.jp ? 1 : 0)}/{(glyphs.ContainsKey((x.c, x.form)) ? "HIT" : "MISS")}/w{(glyphs.TryGetValue((x.c, x.form), out var gg) ? gg.w : -1)}"
                    : $"{x.c}/LATIN")));
            Console.WriteLine("alpha misses: " + string.Join(", ",
                Alpha.Where(c => !glyphs.ContainsKey((c, 0)))));
            var strip = new Bitmap(700, CH, PixelFormat.Format32bppArgb);
            using (var gr = Graphics.FromImage(strip))
            {
                gr.Clear(Color.Transparent);
                gr.FillRectangle(new SolidBrush(Color.FromArgb(70, 255, 255, 255)), 0, BaseY - 13, 700, 1);
                gr.FillRectangle(new SolidBrush(Color.FromArgb(150, 255, 60, 60)), 0, BaseY, 700, 1);
                gr.FillRectangle(new SolidBrush(Color.FromArgb(70, 255, 255, 255)), 0, 23, 700, 1);
            }
            float e1 = ComposeVisual(ToVisual(Shape(Phrase)), strip, rgbNew, listNew, charCell, glyphs, BaseY, BaseY, 6, KeepShift);
            var iso = Alpha.Select(ch => (ch, 0, false)).ToList();
            var strip2 = new Bitmap(700, CH, PixelFormat.Format32bppArgb);
            using (var gr = Graphics.FromImage(strip2))
            {
                gr.Clear(Color.Transparent);
                gr.FillRectangle(new SolidBrush(Color.FromArgb(70, 255, 255, 255)), 0, BaseY - 13, 700, 1);
                gr.FillRectangle(new SolidBrush(Color.FromArgb(150, 255, 60, 60)), 0, BaseY, 700, 1);
                gr.FillRectangle(new SolidBrush(Color.FromArgb(70, 255, 255, 255)), 0, 23, 700, 1);
            }
            float e2 = ComposeVisual(iso, strip2, rgbNew, listNew, charCell, glyphs, BaseY, BaseY, 6, KeepShift);
            Console.WriteLine($"compose: phrase end={e1:F1}  alpha end={e2:F1}");
            int vw = (int)Math.Max(e1, e2) + 8;
            var verify = new Bitmap(vw, CH * 2 + 6, PixelFormat.Format32bppArgb);
            using (var g2 = Graphics.FromImage(verify))
            {
                g2.Clear(Color.FromArgb(25, 25, 30));
                g2.DrawImage(strip, 0, 0);
                g2.DrawImage(strip2, 0, CH + 6);
            }
            var up = Upscale(verify, 4);
            var outPng = Path.Combine(outDir, "verify_phrase.png");
            up.Save(outPng, ImageFormat.Png);
            Console.WriteLine($"wrote {outPng} ({up.Width}x{up.Height})");
            report.AppendLine($"visual: {outPng}");
        }
        else
        {
            report.AppendLine("outputs: NOT WRITTEN (checks failed)");
        }
        report.AppendLine($"RESULT: {(fail == 0 ? "ALL PASS" : fail + " FAILURES")}");
        var reportPath = Path.Combine(outDir, "BUILD_REPORT.txt");
        Directory.CreateDirectory(outDir);
        File.WriteAllText(reportPath, report.ToString());
        Console.WriteLine($"wrote {reportPath}");
        Console.WriteLine($"RESULT: {(fail == 0 ? "ALL PASS" : fail + " FAILURES")}");
        return fail == 0 ? 0 : 1;
    }

    // ================= rt: byte-level codec round-trip =================
    static int Rt()
    {
        int fail = 0;
        void T(bool ok, string name, string detail = "")
        {
            Console.WriteLine($"  [{(ok ? "PASS" : "FAIL")}] {name}{(detail.Length > 0 ? " — " + detail : "")}");
            if (!ok) fail++;
        }
        void Throws(Action a, string name)
        {
            try { a(); T(false, name, "no exception thrown"); }
            catch (Exception e) { T(true, name, e.Message); }
        }
        static string Esc(string s) => s.Replace("\n", "\\n");

        // tables
        var arabicEnc = new Dictionary<(char letter, int form), int>();   // (letter,form) -> cell
        var arabicDec = new Dictionary<int, (char letter, int form)>();   // cell -> (letter,form)
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\allocation.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            var key = (p[0][0], int.Parse(p[2]));
            int cell = int.Parse(p[4]);
            arabicEnc[key] = cell;
            arabicDec[cell] = key;
        }
        var cellToChar = new Dictionary<int, char>();                     // decode non-Arabic
        var charToCell = new Dictionary<char, int>();                     // encode non-Arabic (safe cells only)
        int multiCharCells = 0;
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length < 11 || p[10] != "GLYPH") continue;
            int cell = int.Parse(p[1]);
            if (cell < 0) continue;
            if (p[5].Length != 1) { if (p[5].Length > 1) multiCharCells++; continue; }
            char ch = p[5][0];
            cellToChar[cell] = ch;
            // encode map skips cells that now hold Arabic (sacrificed chars) — first cell wins
            if (!arabicDec.ContainsKey(cell) && !charToCell.ContainsKey(ch)) charToCell[ch] = cell;
        }
        Console.WriteLine($"tables: arabic={arabicEnc.Count} cells, latin-safe chars={charToCell.Count}, " +
                          $"single-char cells={cellToChar.Count}, multi-char cells skipped={multiCharCells}");

        byte[] Encode(string s)
        {
            var res = new List<byte>();
            foreach (var (c, form, _) in ToVisual(Shape(s)))
            {
                if (form >= 0)
                {
                    if (!arabicEnc.TryGetValue((c, form), out var cell))
                        throw new Exception($"no allocated glyph for '{c}' form {form} (U+{(int)c:X4})");
                    res.Add((byte)(cell + 0x20));
                }
                else if (c == ' ') res.Add(0x01);
                else if (c == '\n') res.Add(0x02);
                else
                {
                    if (!charToCell.TryGetValue(c, out var cell))
                        throw new Exception($"no safe cell for U+{(int)c:X4} '{c}' (sacrificed/forbidden/unsupported)");
                    res.Add((byte)(cell + 0x20));
                }
            }
            return res.ToArray();
        }

        string Decode(byte[] bytes)
        {
            var items = new List<(char c, int form, bool jp)>();
            foreach (var b in bytes)
            {
                if (b == 0x01) { items.Add((' ', -1, false)); continue; }
                if (b == 0x02) { items.Add(('\n', -1, false)); continue; }
                int cell = b - 0x20;
                if (cell < 0) throw new Exception($"control byte 0x{b:X2} (only 01=space, 02=newline)");
                if (arabicDec.TryGetValue(cell, out var a)) { items.Add((a.letter, a.form, false)); continue; }
                if (cellToChar.TryGetValue(cell, out var ch)) { items.Add((ch, -1, false)); continue; }
                throw new Exception($"cell {cell} (byte 0x{b:X2}) has no char (forbidden/unsupported/multi-char)");
            }
            return new string(ToVisual(items).Select(x => x.c).ToArray());
        }

        Console.WriteLine("\n== rt: encoder evidence ==");
        var b1 = Encode("A A");
        T(b1.SequenceEqual(new byte[] { 0x2E, 0x01, 0x2E }),
            "encode(\"A A\") == 2E 01 2E (engine bytes, state model)",
            string.Join(" ", b1.Select(x => x.ToString("X2"))));
        T(Decode(new byte[] { 0x2E, 0x01, 0x2E }) == "A A", "decode(2E 01 2E) == \"A A\"");

        Console.WriteLine("\n== rt: logical round-trips ==");
        string[] samples =
        {
            "", " ", "\n",
            "السلام عليكم",
            "مرحبا بالعالم",
            "بسم الله الرحمن الرحيم",
            "المرحلة 2 ناجحة",
            "أآؤإء",
            "1234567890",
            "!?,.",
            "P W A S T M I H",
            "سطر أول 1\nسطر ثاني 2",
        };
        foreach (var s in samples)
        {
            try
            {
                var b = Encode(s);
                var back = Decode(b);
                T(back == s, $"decode(encode(\"{Esc(s)}\")) == original",
                    back == s ? $"{b.Length} bytes" : $"got \"{Esc(back)}\" ({b.Length} bytes)");
                var b2 = Encode(back);
                T(b2.SequenceEqual(b), $"encode(decode(bytes)) == bytes for \"{Esc(s)}\"",
                    b2.SequenceEqual(b) ? "" : $"got [{string.Join(" ", b2.Select(x => x.ToString("X2")))}]");
            }
            catch (Exception e) { T(false, $"round-trip \"{Esc(s)}\"", e.Message); }
        }

        Console.WriteLine("\n== rt: loud failures ==");
        Throws(() => Encode("abc"), "encode(\"abc\") rejects sacrificed latin");
        Throws(() => Encode("A B"), "encode(\"A B\") rejects sacrificed 'B' (cell 15 = Arabic ى)");
        var by = Encode("ى");
        T(Decode(by) == "ى", "encode(\"ى\") round-trips (U+0649 now allocated)",
            $"{by.Length} bytes [{string.Join(" ", by.Select(x => x.ToString("X2")))}]");
        Throws(() => Encode("\t"), "encode(\"\\t\") rejects unsupported control");
        Throws(() => Decode(new byte[] { 0x00 }), "decode(00) rejects control byte");
        Throws(() => Decode(new byte[] { 0x72 }), "decode(72) rejects forbidden cell 78");
        Throws(() => Decode(new byte[] { 0xFF }), "decode(FF) rejects forbidden cell 223");

        Console.WriteLine("\n== rt: state repositioning ==");
        {
            // tokenize+shape a natural string, and the state every content item must be DRAWN with
            (List<(char c, int form, bool jp)> items, List<byte[]> raws, Dictionary<int, string> want)
                Logical(string s, byte[] pre)
            {
                var raws = new List<byte[]>();
                var flat = new StringBuilder();
                int i = 0;
                while (i < s.Length)
                {
                    if (s[i] == '<' && MsgTryToken(s, i, out var tl, out var raw))
                    { flat.Append((char)(0xE000 + raws.Count)); raws.Add(raw); i += tl; }
                    else if (s[i] == '<' && MsgTryCellToken(s, i, out var cl, out var cel))
                    { flat.Append((char)(0xE000 + raws.Count)); raws.Add(new byte[] { (byte)(cel + 0x20) }); i += cl; }
                    else { flat.Append(s[i]); i++; }
                }
                var items = Shape(flat.ToString());
                var st = new Dictionary<byte, byte[]>();
                for (int j = 0; j < pre.Length && MsgIsCmd(pre[j]);)
                {
                    if (!MsgCmdSize.TryGetValue(pre[j], out var psz)) break;
                    if (IsStateOpenerCode(pre[j]) || IsStateCloserCode(pre[j]))
                        ApplyStateCmd(st, pre.AsSpan(j, 1 + psz).ToArray());
                    j += 1 + psz;
                }
                var want = new Dictionary<int, string>();
                for (int k = 0; k < items.Count; k++)
                {
                    char ch = items[k].c;
                    if (ch >= 0xE000 && ch <= 0xF8FF && raws[ch - 0xE000].Length > 0 && raws[ch - 0xE000][0] < 0x20)
                    {
                        byte code = raws[ch - 0xE000][0];
                        if (IsStateOpenerCode(code) || IsStateCloserCode(code)) ApplyStateCmd(st, raws[ch - 0xE000]);
                        // non-state commands (PrintIcon/Delay/Clear) draw nothing here
                    }
                    else want[k] = StateSig(st);
                }
                return (items, raws, want);
            }

            // walk the encoded bytes: the state actually active at each drawn glyph
            List<(char c, string st)> Drawn(byte[] b)
            {
                var st = new Dictionary<byte, byte[]>();
                var outp = new List<(char, string)>();
                for (int j = 0; j < b.Length;)
                {
                    byte x = b[j];
                    if (x == 0x01) { outp.Add((' ', StateSig(st))); j++; continue; }
                    if (x == 0x02) { outp.Add(('\n', StateSig(st))); j++; continue; }
                    if (x == 0x00) { j++; continue; }
                    if (MsgIsCmd(x))
                    {
                        if (!MsgCmdSize.TryGetValue(x, out var sz)) throw new Exception($"unknown command 0x{x:X2}");
                        if (IsStateOpenerCode(x) || IsStateCloserCode(x))
                            ApplyStateCmd(st, b.AsSpan(j, 1 + sz).ToArray());
                        j += 1 + sz;
                        continue;
                    }
                    int cell = x - 0x20;
                    char ch = arabicDec.TryGetValue(cell, out var a) ? a.letter
                            : cellToChar.TryGetValue(cell, out var l) ? l : '?';
                    outp.Add((ch, StateSig(st)));
                    j++;
                }
                return outp;
            }

            byte[] prefix = { 0x09, 0x0A, 0x07, 0xFF, 0x00, 0x00, 0x80 };   // icon + red, kept at byte 0
            string[] stateSamples =
            {
                "السلام يا <C 07 00 FF 00 80>النار<C 03> عادي",
                "السلام<C 03> يا <C 07 00 FF 00 80>النار<C 03> عادي",
                "<C 07 00 FF 00 80>الأول<C 03> الثاني <C 07 FF FF 00 80>الثالث<C 03> الرابع",
                "سطر أول <C 0B 5A>ضيق\nسطر <C 0B 64>عريض<C 03> نهاية",
                "لا أوامر حالة هنا إطلاقا",
            };
            foreach (var nat in stateSamples)
            {
                string name = $"state while drawing == state in reading order — \"{Esc(nat)}\"";
                try
                {
                    var (items, raws, want) = Logical(nat, prefix);
                    char G(int k)
                    {
                        char ch = items[k].c;
                        if (ch >= 0xE000 && ch <= 0xF8FF)
                        {
                            int cell = raws[ch - 0xE000][0] - 0x20;
                            return arabicDec.TryGetValue(cell, out var a) ? a.letter
                                 : cellToChar.TryGetValue(cell, out var l) ? l : '?';
                        }
                        return ch;
                    }
                    var order = ToVisualOrder(items, HardSet(raws)).Where(want.ContainsKey).ToArray();
                    var expected = order.Select(k => (G(k), want[k])).ToList();
                    var arNorm = FixState(nat, prefix);
                    var bytes = prefix.Concat(EncodeMsg(arNorm, arabicEnc, charToCell)).ToArray();
                    var drawn = Drawn(bytes);
                    bool same = drawn.Count == expected.Count &&
                                expected.Zip(drawn).All(z => z.First.Item1 == z.Second.c && z.First.Item2 == z.Second.st);
                    string detail = same ? $"{drawn.Count} glyphs, states match" : $"count {drawn.Count}/{expected.Count}";
                    if (!same)
                    {
                        for (int q = 0; q < Math.Min(expected.Count, drawn.Count); q++)
                            if (expected[q].Item1 != drawn[q].c || expected[q].Item2 != drawn[q].st)
                            { detail += $" | first diff @ {q}: expected '{expected[q].Item1}' [{expected[q].Item2}] got '{drawn[q].c}' [{drawn[q].st}]"; break; }
                        detail += $" | arNorm=\"{Esc(arNorm)}\" | bytes={string.Join(" ", bytes.Select(x => x.ToString("X2")))}";
                    }
                    T(same, name, detail);
                }
                catch (Exception e) { T(false, name, e.Message); }
            }
        }

        Console.WriteLine("\n== rt: page boundaries (Clear/Delay are hard boundaries, commands keep logical position) ==");
        {
            // property: encode(whole) == concat(encode(page_i), command_i)  — no run reversal across a command
            string[] pageSamples =
            {
                "ما يزعجني حقا<C 14 58 00><C 10>هو أنه يدور ويقول\nلكل الناس أننا اللصوص!<C 14 C3 00> <C 10> <C 14 14 00><C 10>الآن المدينة",
                "حسنا<C 14 58 00><C 10>!",
                "هل غضبت?<C 14 B4 00><C 10> <C 14 0A 00><C 10>أنا لم أغضب.<C 14 32 00><C 10>لا, إطلاقا.",
                "أولا, علينا تبرئة أسمائنا.<C 14 97 00><C 10> <C 14 18 00><C 10>عندما نجد المتسبب",
                "<C 14 E1 00><C 10>لدينا حساب\nيجب تسويته<C 14 A6 00><C 10>وإذا كان",
            };
            var rx = new System.Text.RegularExpressions.Regex(@"(<C (?:10|14 [0-9A-F]{2} [0-9A-F]{2}|17 [0-9A-F ]+)>)");
            foreach (var s in pageSamples)
            {
                string name = $"page boundaries keep order — \"{Esc(s)}\"";
                try
                {
                    var whole = EncodeMsg(s, arabicEnc, charToCell);
                    var exp = new List<byte>();
                    foreach (var piece in rx.Split(s))
                    {
                        if (piece.Length == 0) continue;
                        if (MsgTryToken(piece, 0, out var tl, out var raw) && tl == piece.Length) exp.AddRange(raw);
                        else exp.AddRange(EncodeMsg(piece, arabicEnc, charToCell));
                    }
                    T(whole.SequenceEqual(exp), name, whole.SequenceEqual(exp) ? $"{whole.Length} bytes" : "bytes differ from per-page encode");
                    var cmdsWhole = new List<string>();
                    for (int j = 0; j < whole.Length;)
                    {
                        if (MsgIsCmd(whole[j])) { int sz = MsgCmdSize[whole[j]]; cmdsWhole.Add(Convert.ToHexString(whole.AsSpan(j, 1 + sz))); j += 1 + sz; }
                        else j++;
                    }
                    var cmdsLogical = rx.Matches(s).Select(m => { MsgTryToken(m.Value, 0, out _, out var r2); return Convert.ToHexString(r2); }).ToList();
                    T(cmdsWhole.SequenceEqual(cmdsLogical), "  command order == logical command order");
                }
                catch (Exception e) { T(false, name, e.Message); }
            }
            // inline commands (icon) are NOT boundaries: RTL run order still crosses them
            {
                string s = "حدد <C 09 DF> ملف";
                var whole = EncodeMsg(s, arabicEnc, charToCell);
                var exp = EncodeMsg("ملف", arabicEnc, charToCell).Concat(new byte[] { 0x01, 0x09, 0xDF, 0x01 })
                    .Concat(EncodeMsg("حدد", arabicEnc, charToCell)).ToArray();
                T(whole.SequenceEqual(exp), "inline icon command is not a boundary (runs reverse across it)");
            }
            // <X nn> cell tokens are content, never boundaries
            {
                string s = "منظمة <X 5E> مهمة";
                var whole = EncodeMsg(s, arabicEnc, charToCell);
                var exp = EncodeMsg("مهمة", arabicEnc, charToCell).Concat(new byte[] { 0x01, 0x7E, 0x01 })
                    .Concat(EncodeMsg("منظمة", arabicEnc, charToCell)).ToArray();
                T(whole.SequenceEqual(exp), "<X 5E> cell token is content (runs reverse across it)");
            }
        }

        Console.WriteLine("\n== rt: lam-alef ligature (tt/evt only; explicit ligCell=36, default = off) ==");
        {
            const int LC = 36;
            byte lb = (byte)(LC + 0x20);
            byte[] E(string x, bool lig) => lig ? EncodeMsg(x, arabicEnc, charToCell, LC) : EncodeMsg(x, arabicEnc, charToCell);
            T(E("لا", false).Length == 2 && !E("لا", false).Contains(lb), "default (ligature off): \"لا\" = 2 glyph bytes, unchanged");
            T(E("لا", true).SequenceEqual(new[] { lb }), "\"لا\" -> single ligature byte");
            T(E("ولا", true).SequenceEqual(new[] { lb }.Concat(E("و", false))), "\"ولا\": lig then و (RTL order kept)");
            T(!E("فلا", true).Contains(lb) && E("فلا", true).SequenceEqual(E("فلا", false)), "\"فلا\": lam is MED (joined) -> no ligature, bytes identical to off");
            T(!E("لأ", true).Contains(lb) && !E("لإ", true).Contains(lb) && !E("لآ", true).Contains(lb), "hamza/madda variants are NOT mapped to the plain ligature");
            T(!E("لم", true).Contains(lb) && E("لم", true).SequenceEqual(E("لم", false)), "lam not followed by alef untouched");
            T(E("لا<C 14 32 00><C 10>لا", true).Count(x => x == lb) == 2, "two ligatures across a page boundary command");
            T(E("لا, إطلاقا.", true).Count(x => x == lb) == 1 && E("لا, إطلاقا.", true).Length == E("لا, إطلاقا.", false).Length - 1, "\"لا, إطلاقا.\": one ligature, one byte shorter");
            T(E("الله", true).SequenceEqual(E("الله", false)), "\"الله\" (ا ISO + لل) unchanged");
        }

        Console.WriteLine($"\nRESULT: {(fail == 0 ? "ALL PASS" : fail + " FAILURES")}");
        return fail == 0 ? 0 : 1;
    }

    // ================= batch: translate selected messages + rebuild sys.bar =================
    static int Batch(string tsvPath)
    {
        const string ModBar = @"<OPENKH_DIR>\mod\kh2\msg\us\sys.bar";
        const string ExpectedListSha = "5ddc337bbfdfc44165521bfe39f4f73edcb1f4585c962a3d4af99d50a24f87dd";   // P3 digit x1.05 regenerated sys.list
        const int MsgCount = 3357;
        string tsv = tsvPath ?? Path.Combine(Root, @"translation\batch1.tsv");
        string origBarPath = Path.Combine(Root, @"technical\extracted\game-data\original\msg\us\sys.bar");
        string origListPath = Path.Combine(Root, @"technical\extracted\bar\us\fontinfo\sys.list");
        string outDir = Path.Combine(Root, @"font-rtl\arabic\out");
        string newListPath = Path.Combine(outDir, "sys.list");
        string outBarPath = Path.Combine(outDir, "sys.bar");
        string reportPath = Path.Combine(Root, @"translation\" + Path.GetFileNameWithoutExtension(tsv) + "_table.tsv");

        int fail = 0;
        void Check(bool ok, string msg) { Console.WriteLine($"  [{(ok ? "PASS" : "FAIL")}] {msg}"); if (!ok) fail++; }

        // --- codec tables (same as rt) ---
        var arabicEnc = new Dictionary<(char letter, int form), int>();
        var arabicDec = new Dictionary<int, (char letter, int form)>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\allocation.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            var key = (p[0][0], int.Parse(p[2]));
            int cell = int.Parse(p[4]);
            arabicEnc[key] = cell;
            arabicDec[cell] = key;
        }
        var cellToChar = new Dictionary<int, char>();   // original mapping (incl. sacrificed cells)
        var charToCell = new Dictionary<char, int>();   // encode-safe (excludes sacrificed cells)
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length < 11 || p[10] != "GLYPH") continue;
            int cell = int.Parse(p[1]);
            if (cell < 0 || p[5].Length != 1) continue;
            char ch = p[5][0];
            cellToChar[cell] = ch;
            if (!arabicDec.ContainsKey(cell) && !charToCell.ContainsKey(ch)) charToCell[ch] = cell;
        }

        byte[] Encode(string s) => EncodeMsg(s, arabicEnc, charToCell, -1, -1, AltPeriodOn ? AltPeriodCell : -1);

        string DecodeAr(byte[] bytes)
        {
            var items = new List<(char c, int form, bool jp)>();
            var map = new Dictionary<char, byte[]>();
            var cells = new Dictionary<char, int>();
            int si = 0, ci = 0;
            for (int b = 0; b < bytes.Length;)
            {
                byte x = bytes[b];
                if (x == 0x01) { items.Add((' ', -1, false)); b++; continue; }
                if (x == 0x02) { items.Add(('\n', -1, false)); b++; continue; }
                if (MsgIsCmd(x))
                {
                    if (!MsgCmdSize.TryGetValue(x, out var n)) throw new Exception($"no size for command 0x{x:X2}");
                    if (b + n >= bytes.Length) throw new Exception($"truncated command 0x{x:X2}");
                    char sc = (char)(0xE000 + si++);
                    map[sc] = bytes.AsSpan(b, n + 1).ToArray();
                    items.Add((sc, -1, false));
                    b += n + 1;
                    continue;
                }
                int cell = x - 0x20;
                if (cell < 0) throw new Exception($"control byte 0x{x:X2}");
                if (arabicDec.TryGetValue(cell, out var a)) { items.Add((a.letter, a.form, false)); b++; continue; }
                if (cell == AltPeriodCell && AltPeriodOn) { items.Add(('.', -1, false)); b++; continue; }
                    if (cellToChar.TryGetValue(cell, out var ch)) { items.Add((ch, -1, false)); b++; continue; }
                char cc = (char)(0xE100 + ci++);
                cells[cc] = cell;
                items.Add((cc, -1, false));
                b++;
            }
            var sb = new StringBuilder();
            foreach (var (c, _, _) in ToVisual(items, HardOfMap(map)))
                sb.Append(c >= 0xE000 && c <= 0xE0FF ? MsgCmdToken(map[c], 0)
                    : c >= 0xE100 && c <= 0xE1FF ? MsgCellToken(cells[c])
                    : c.ToString());
            return sb.ToString();
        }

        double Width(byte[] msg, int start, int end, byte[] sp, string tag)
        {
            double w = 0;
            int i = start;
            while (i < end)
            {
                byte b = msg[i];
                if (b == 0x01) { w += 5; i++; continue; }       // space advance (same both sides)
                if (b == 0x02) { i++; continue; }               // newline: no advance
                if (b == 0x00) break;
                if (MsgIsCmd(b))
                {
                    if (!MsgCmdSize.TryGetValue(b, out var n) || i + n >= end)
                    { Console.WriteLine($"  [FAIL] {tag}: bad command 0x{b:X2} in text span"); fail++; break; }
                    i += n + 1;
                    continue;
                }
                int cell = b - 0x20;
                if (cell < 0 || cell >= 280) { Console.WriteLine($"  [FAIL] {tag}: control byte 0x{b:X2} in text span"); fail++; break; }
                w += sp[cell] / 2.0;
                i++;
            }
            return w;
        }

        // --- batch rows ---
        var rows = new List<(int id, string en, string ar)>();
        foreach (var line in File.ReadLines(tsv))
        {
            if (line.Trim().Length == 0) continue;
            var p = line.Split('\t');
            if (p.Length != 3) { Console.WriteLine($"  [FAIL] bad tsv row: {line}"); fail++; continue; }
            rows.Add((int.Parse(p[0]), p[1].Replace("\\n", "\n"), p[2].Replace("\\n", "\n")));   // literal \n = newline (line-based TSV)
        }
        var batchIds = rows.Select(r => r.id).ToHashSet();
        Console.WriteLine($"batch: {rows.Count} rows, {batchIds.Count} unique ids from {Path.GetFileName(tsv)}");

        // --- parse original sys.bar ---
        var bar = File.ReadAllBytes(origBarPath);
        Check(bar.Length >= 48 && System.Text.Encoding.ASCII.GetString(bar, 0, 3) == "BAR",
            $"orig bar: BAR magic, size={bar.Length}");
        uint entryCount = BitConverter.ToUInt32(bar, 4);
        uint sysOff = BitConverter.ToUInt32(bar, 24), sysLen = BitConverter.ToUInt32(bar, 28);
        uint mdOff = BitConverter.ToUInt32(bar, 40), mdLen = BitConverter.ToUInt32(bar, 44);
        Check(entryCount == 2 && sysOff == 48 && mdLen == 0 && mdOff == ((sysOff + sysLen + 15) & ~15u),
            $"orig bar: entries=2 sys=({sysOff},{sysLen}) md_m=({mdOff},{mdLen}) aligned16");
        byte[] msg0 = bar.AsSpan((int)sysOff, (int)sysLen).ToArray();

        // --- parse msg blob ---
        uint mmagic = BitConverter.ToUInt32(msg0, 0);
        uint mcount = BitConverter.ToUInt32(msg0, 4);
        Check(mmagic == 1 && mcount == MsgCount, $"msg: magic={mmagic} count={mcount} (expect 1/{MsgCount})");
        var ids = new int[mcount];
        var offs = new uint[mcount];
        for (int i = 0; i < mcount; i++)
        {
            ids[i] = (int)BitConverter.ToUInt32(msg0, 8 + i * 8);
            offs[i] = BitConverter.ToUInt32(msg0, 8 + i * 8 + 4);
        }
        bool sorted = true;
        for (int i = 1; i < mcount; i++) if (offs[i] < offs[i - 1]) { sorted = false; break; }
        Check(sorted && offs[0] == 8 + mcount * 8, $"table sorted asc, firstOff={offs[0]} (expect {8 + mcount * 8})");
        var origMsgs = new byte[mcount][];
        int badEnd = 0, interiorZero = 0;
        for (int i = 0; i < mcount; i++)
        {
            int start = (int)offs[i];
            int end = i + 1 < mcount ? (int)offs[i + 1] : (int)sysLen;
            var m = msg0.AsSpan(start, end - start).ToArray();
            origMsgs[i] = m;
            if (m.Length == 0 || m[^1] != 0x00) badEnd++;
            if (m.Take(m.Length - 1).Contains((byte)0x00)) interiorZero++;
        }
        Check(badEnd == 0, $"all {mcount} messages end with 0x00 (badEnd={badEnd})");
        Console.WriteLine($"  [INFO] {interiorZero} messages contain 0x00 before last byte (command operands, e.g. Position — legitimate)");
        var idToIdx = new Dictionary<int, int>();
        for (int i = 0; i < mcount; i++) idToIdx[ids[i]] = i;

        // --- sp tables ---
        var spOrig = File.ReadAllBytes(origListPath);
        var spNew = File.ReadAllBytes(newListPath);
        Check(spOrig.Length == 280 && Sha256Str(spNew) == ExpectedListSha,
            $"sys.list orig=280 bytes, out sha={Sha256Str(spNew).Substring(0, 8)}… (expect {ExpectedListSha.Substring(0, 8)}…)");

        // --- process rows: EN match + AR encode + roundtrip + widths ---
        var replaced = new Dictionary<int, byte[]>();   // id -> full new message (prefix + AR bytes + End)
        var report = new StringBuilder();
        report.AppendLine("id\ten\tar\tar_px\ten_px\tratio_pct\tstatus");
        int enMismatch = 0, rtFail = 0, encFail = 0, over = 0, over100 = 0;
        foreach (var (id, en, ar) in rows)
        {
            if (!idToIdx.TryGetValue(id, out var idx))
            { Console.WriteLine($"  [FAIL] id {id} not in msg (en={en})"); fail++; continue; }
            string status = "OK";
            var m = origMsgs[idx];
            int textStart, textEnd = m.Length - 1;               // last byte = End (0x00), verified above
            string enBack;
            try
            {
                textStart = MsgSkipLeading(m);
                enBack = MsgDecodeEn(m, textStart, textEnd, cellToChar);
            }
            catch (Exception e)
            { enMismatch++; fail++; Console.WriteLine($"  [FAIL] id {id} EN decode: {e.Message}"); continue; }
            if (enBack != en)
            { enMismatch++; fail++; status = "EN_MISMATCH"; Console.WriteLine($"  [FAIL] id {id} EN mismatch: msg=\"{enBack}\" tsv=\"{en}\""); }
            byte[] arBytes = null;
            string arNorm = ar;                                   // ى now allocated (U+0649 FEEF/FEF0 — was substituted to ي)
            try { arNorm = FixState(ar, m.AsSpan(0, textStart).ToArray()); arBytes = Encode(arNorm); }
            catch (Exception e) { encFail++; fail++; status = "ENC_FAIL"; Console.WriteLine($"  [FAIL] id {id} EN={en}: {e.Message}"); }
            if (arBytes != null)
            {
                try
                {
                    string rt = DecodeAr(arBytes);
                    if (rt != arNorm) { rtFail++; fail++; status = "RT_FAIL"; Console.WriteLine($"  [FAIL] id {id} roundtrip mismatch (en={en})"); }
                }
                catch (Exception e) { rtFail++; fail++; status = "RT_FAIL"; Console.WriteLine($"  [FAIL] id {id} roundtrip: {e.Message}"); }
                replaced[id] = m.Take(textStart).Concat(arBytes).Concat(new byte[] { 0x00 }).ToArray();
            }
            double arPx = arBytes != null ? Width(replaced[id], textStart, textStart + arBytes.Length, spNew, $"id {id}") : 0;
            double enPx = Width(m, textStart, textEnd, spOrig, $"id {id}");
            double ratio = enPx > 0 ? arPx / enPx * 100 : 0;
            if (arBytes != null && ratio > 100) over100++;
            if (arBytes != null && ratio > 150) { over++; if (status == "OK") status = "WARN_OVER_150"; }
            report.AppendLine(string.Join("\t", id, en.Replace("\n", "\\n"), ar.Replace("\n", "\\n"),
                arPx.ToString("F1"), enPx.ToString("F1"), ratio.ToString("F0"), status));
        }
        Check(enMismatch == 0, $"EN text matches original bytes for all {rows.Count} rows (bad={enMismatch})");
        Check(encFail == 0 && rtFail == 0, $"AR encode + roundtrip OK (encFail={encFail} rtFail={rtFail})");
        Check(replaced.Count == rows.Count, $"all {rows.Count} rows encoded");
        Console.WriteLine($"  [INFO] width >100% of EN: {over100} rows, >150% (WARN): {over} rows (see {Path.GetFileName(reportPath)})");

        // --- rebuild msg payload (non-batch byte-identical) ---
        var outMsgs = new byte[mcount][];
        var newOffs = new uint[mcount];
        uint run = 8 + mcount * 8;
        for (int i = 0; i < mcount; i++)
        {
            outMsgs[i] = replaced.TryGetValue(ids[i], out var nw) ? nw : origMsgs[i];
            newOffs[i] = run;
            run += (uint)outMsgs[i].Length;
        }
        var payload = new byte[run];
        BitConverter.GetBytes(1u).CopyTo(payload, 0);
        BitConverter.GetBytes(mcount).CopyTo(payload, 4);
        for (int i = 0; i < mcount; i++)
        {
            BitConverter.GetBytes((uint)ids[i]).CopyTo(payload, 8 + i * 8);
            BitConverter.GetBytes(newOffs[i]).CopyTo(payload, 8 + i * 8 + 4);
            outMsgs[i].CopyTo(payload, (int)newOffs[i]);
        }
        int nonBatchDiff = 0;
        for (int i = 0; i < mcount; i++)
            if (!batchIds.Contains(ids[i]) && !origMsgs[i].AsSpan().SequenceEqual(outMsgs[i])) nonBatchDiff++;
        Check(nonBatchDiff == 0, $"non-batch messages byte-identical to original (changed: {nonBatchDiff})");

        // --- rebuild bar file ---
        int newSysLen = payload.Length;
        int newMdOff = ((48 + newSysLen + 15) & ~15);
        var nb = new byte[newMdOff];                    // md_m len=0: file ends at its (aligned) offset, like original
        Array.Copy(bar, 0, nb, 0, 48);                  // header + entry table verbatim
        BitConverter.GetBytes((uint)newSysLen).CopyTo(nb, 28);
        BitConverter.GetBytes((uint)newMdOff).CopyTo(nb, 40);
        payload.CopyTo(nb, 48);
        Check(nb.Length == newMdOff && newMdOff - 48 >= newSysLen,
            $"built bar: size={nb.Length} sys=(48,{newSysLen}) md_m=({newMdOff},0)");

        // --- reparse built bar independently ---
        {
            uint bCount = BitConverter.ToUInt32(nb, 4);
            uint bOff = BitConverter.ToUInt32(nb, 24), bLen = BitConverter.ToUInt32(nb, 28);
            uint bMd = BitConverter.ToUInt32(nb, 40), bMdLen = BitConverter.ToUInt32(nb, 44);
            var bp = nb.AsSpan((int)bOff, (int)bLen).ToArray();
            uint bMagic = BitConverter.ToUInt32(bp, 0);
            uint bMsgCount = BitConverter.ToUInt32(bp, 4);
            bool ok = bCount == 2 && bOff == 48 && bMagic == 1 && bMsgCount == mcount && bMdLen == 0 && bMd == (uint)newMdOff;
            int mismatch = 0;
            for (int i = 0; i < mcount && ok; i++)
            {
                int id = (int)BitConverter.ToUInt32(bp, 8 + i * 8);
                uint o = BitConverter.ToUInt32(bp, 8 + i * 8 + 4);
                uint o2 = i + 1 < mcount ? BitConverter.ToUInt32(bp, 8 + (i + 1) * 8 + 4) : bLen;
                var m = bp.AsSpan((int)o, (int)(o2 - o)).ToArray();
                byte[] want;
                if (batchIds.Contains(id))
                {
                    if (!replaced.TryGetValue(id, out want)) { mismatch++; continue; }
                }
                else want = origMsgs[Array.IndexOf(ids, id)];
                if (!m.AsSpan().SequenceEqual(want)) mismatch++;
            }
            Check(ok && mismatch == 0, $"built bar reparse: structure OK, message mismatch={mismatch}");
        }

        // --- report (always written; UTF-8 no BOM) ---
        Directory.CreateDirectory(Path.GetDirectoryName(reportPath));
        File.WriteAllText(reportPath, report.ToString(), new UTF8Encoding(false));
        Console.WriteLine($"wrote {reportPath}");

        if (fail > 0)
        {
            Console.WriteLine($"RESULT: {fail} FAILURES — nothing written to mod");
            return 1;
        }

        // --- write built bar, backup mod, install ---
        Directory.CreateDirectory(outDir);
        File.WriteAllBytes(outBarPath, nb);
        string builtSha = Sha256Str(nb);
        Console.WriteLine($"built {outBarPath}  size={nb.Length}  sha256={builtSha}");
        if (Environment.GetEnvironmentVariable("KH2_NO_INSTALL") == "1")   // build-only: never touch the mod, never create a backup
        { Console.WriteLine("KH2_NO_INSTALL=1: built only - mod NOT touched"); Console.WriteLine("\nRESULT: BUILD-ONLY PASS"); return 0; }

        string bakPath = ModBar + ".pre-" + Path.GetFileNameWithoutExtension(tsv) + ".bak";
        if (!File.Exists(bakPath))
        {
            File.Copy(ModBar, bakPath);
            Console.WriteLine($"backup created: {bakPath}");
        }
        else Console.WriteLine($"backup already exists: {bakPath}");
        var bakSha = Sha256Str(File.ReadAllBytes(bakPath));
        var curSha = Sha256Str(File.ReadAllBytes(ModBar));
        Console.WriteLine($"  [INFO] mod sys.bar before install sha256={curSha}");
        Console.WriteLine($"  [INFO] backup sha256={bakSha}");

        // non-batch must equal the backed-up mod too (mod == original outside id 480)
        {
            var bak = File.ReadAllBytes(bakPath);
            uint bOff = BitConverter.ToUInt32(bak, 24), bLen = BitConverter.ToUInt32(bak, 28);
            var bp = bak.AsSpan((int)bOff, (int)bLen).ToArray();
            uint bMsgCount = BitConverter.ToUInt32(bp, 4);
            int mismatch = 0;
            for (int i = 0; i < bMsgCount; i++)
            {
                int id = (int)BitConverter.ToUInt32(bp, 8 + i * 8);
                if (batchIds.Contains(id)) continue;
                uint o = BitConverter.ToUInt32(bp, 8 + i * 8 + 4);
                uint o2 = i + 1 < bMsgCount ? BitConverter.ToUInt32(bp, 8 + (i + 1) * 8 + 4) : bLen;
                var m = bp.AsSpan((int)o, (int)(o2 - o)).ToArray();
                int j = Array.IndexOf(ids, id);
                if (j < 0 || !m.AsSpan().SequenceEqual(origMsgs[j])) mismatch++;
            }
            Check(mismatch == 0, $"non-batch messages identical to pre-install backup (mismatch={mismatch})");
        }

        if (fail > 0)
        {
            Console.WriteLine($"RESULT: {fail} FAILURES — mod NOT modified");
            return 1;
        }

        File.WriteAllBytes(ModBar, nb);
        var instSha = Sha256Str(File.ReadAllBytes(ModBar));
        Check(instSha == builtSha, $"installed {ModBar} sha256={instSha}");

        Console.WriteLine($"\nRESULT: ALL PASS ({rows.Count} messages translated, {over} width warnings)");
        return 0;
    }

    // ================= tt.bar batch (Roxas prologue — sys atlas, md_m entry preserved) =================
    // Same pipeline as Batch, but the target is tt.bar: entry 0 holds the message blob and entry 1
    // ("md_m") is a texture that must be copied through byte-identically, and the TSVs are cumulative.
    static int BatchTt(string tsvPath, string barName = null, string countArg = null, string outName = null)
    {
        // generic world-bar target: batchtt <tsv> [bar file name, default tt.bar] [message count, default 1869 for tt.bar / read from header] [output name under out\, default = bar name]
        barName = string.IsNullOrEmpty(barName) ? "tt.bar" : barName;
        outName = string.IsNullOrEmpty(outName) ? barName : outName;
        string ModBar = @"<OPENKH_DIR>\mod\kh2\msg\us\" + barName;
        const string ExpectedListSha = "5ddc337bbfdfc44165521bfe39f4f73edcb1f4585c962a3d4af99d50a24f87dd";   // P3 digit x1.05 regenerated sys.list (shared font)
        string tsv = tsvPath ?? Path.Combine(Root, @"translation\batchtt1.tsv");
        string origBarPath = Path.Combine(Root, @"technical\extracted\game-data\original\msg\us\" + barName);
        int MsgCount;
        if (!string.IsNullOrEmpty(countArg)) MsgCount = int.Parse(countArg);
        else if (barName == "tt.bar") MsgCount = 1869;
        else MsgCount = (int)BitConverter.ToUInt32(File.ReadAllBytes(origBarPath).AsSpan((int)BitConverter.ToUInt32(File.ReadAllBytes(origBarPath), 24) + 4, 4));
        string origListPath = Path.Combine(Root, @"technical\extracted\bar\us\fontinfo\sys.list");
        string outDir = Path.Combine(Root, @"font-rtl\arabic\out");
        string newListPath = Path.Combine(outDir, "sys.list");
        string outBarPath = Path.Combine(outDir, outName); Directory.CreateDirectory(Path.GetDirectoryName(outBarPath));
        string reportPath = Path.Combine(Root, @"translation\" + Path.GetFileNameWithoutExtension(tsv) + "_table.tsv");

        int fail = 0;
        void Check(bool ok, string msg) { Console.WriteLine($"  [{(ok ? "PASS" : "FAIL")}] {msg}"); if (!ok) fail++; }

        // --- codec tables (same as rt) ---
        int ligCell = LamAlefOn ? LamAlefRows()[0].cell : -1;
        int ligFin = LamAlefOn && LamAlefRows().Count > 1 ? LamAlefRows()[1].cell : -1;     // lam-alef ligature cell (tt/evt only), -1 = off
        Console.WriteLine(ligCell >= 0 ? $"  [INFO] lam-alef ligature ON: cell {ligCell} (byte 0x{ligCell + 0x20:X2})" : "  [INFO] lam-alef ligature OFF");
        var arabicEnc = new Dictionary<(char letter, int form), int>();
        var arabicDec = new Dictionary<int, (char letter, int form)>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\allocation.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            var key = (p[0][0], int.Parse(p[2]));
            int cell = int.Parse(p[4]);
            arabicEnc[key] = cell;
            arabicDec[cell] = key;
        }
        var cellToChar = new Dictionary<int, char>();   // original mapping (incl. sacrificed cells)
        var charToCell = new Dictionary<char, int>();   // encode-safe (excludes sacrificed cells)
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length < 11 || p[10] != "GLYPH") continue;
            int cell = int.Parse(p[1]);
            if (cell < 0 || p[5].Length != 1) continue;
            char ch = p[5][0];
            cellToChar[cell] = ch;
            if (!arabicDec.ContainsKey(cell) && cell != ligCell && cell != ligFin && !charToCell.ContainsKey(ch)) charToCell[ch] = cell;
        }

        // popup/help ids (drawn from the SYS atlas, where cell 36 is Latin W): plain lam + alef, no ligature.  list = translation\noliga_ids.txt
        var noLigIds = new HashSet<int>();
        string noLigFile = Path.Combine(Root, @"translation\noliga_ids.txt");
        if (File.Exists(noLigFile)) foreach (var l in File.ReadAllLines(noLigFile)) { var tk = l.Split('#')[0].Trim(); if (int.TryParse(tk, out var nid)) noLigIds.Add(nid); }
        bool noLigNow = false;
        byte[] Encode(string s) => noLigNow ? EncodeMsg(s, arabicEnc, charToCell, -1, -1, AltPeriodOn ? AltPeriodCell : -1) : EncodeMsg(s, arabicEnc, charToCell, ligCell, ligFin);

        string DecodeAr(byte[] bytes)
        {
            var items = new List<(char c, int form, bool jp)>();
            var map = new Dictionary<char, byte[]>();
            var cells = new Dictionary<char, int>();
            int si = 0, ci = 0;
            for (int b = 0; b < bytes.Length;)
            {
                byte x = bytes[b];
                if (x == 0x01) { items.Add((' ', -1, false)); b++; continue; }
                if (x == 0x02) { items.Add(('\n', -1, false)); b++; continue; }
                if (MsgIsCmd(x))
                {
                    if (!MsgCmdSize.TryGetValue(x, out var n)) throw new Exception($"no size for command 0x{x:X2}");
                    if (b + n >= bytes.Length) throw new Exception($"truncated command 0x{x:X2}");
                    char sc = (char)(0xE000 + si++);
                    map[sc] = bytes.AsSpan(b, n + 1).ToArray();
                    items.Add((sc, -1, false));
                    b += n + 1;
                    continue;
                }
                int cell = x - 0x20;
                if (cell < 0) throw new Exception($"control byte 0x{x:X2}");
                if (cell == ligFin) { items.Add(('\u0627', Ar.FIN, false)); items.Add(('\u0644', Ar.MED, false)); b++; continue; }
                if (cell == ligCell) { items.Add(('\u0627', Ar.FIN, false)); items.Add(('\u0644', Ar.INI, false)); b++; continue; }
                if (arabicDec.TryGetValue(cell, out var a)) { items.Add((a.letter, a.form, false)); b++; continue; }
                if (cell == AltPeriodCell && AltPeriodOn) { items.Add(('.', -1, false)); b++; continue; }
                    if (cellToChar.TryGetValue(cell, out var ch)) { items.Add((ch, -1, false)); b++; continue; }
                char cc = (char)(0xE100 + ci++);
                cells[cc] = cell;
                items.Add((cc, -1, false));
                b++;
            }
            var sb = new StringBuilder();
            foreach (var (c, _, _) in ToVisual(items, HardOfMap(map)))
                sb.Append(c >= 0xE000 && c <= 0xE0FF ? MsgCmdToken(map[c], 0)
                    : c >= 0xE100 && c <= 0xE1FF ? MsgCellToken(cells[c])
                    : c.ToString());
            return sb.ToString();
        }

        double Width(byte[] msg, int start, int end, byte[] sp, string tag)
        {
            double w = 0;
            int i = start;
            while (i < end)
            {
                byte b = msg[i];
                if (b == 0x01) { w += 5; i++; continue; }       // space advance (same both sides)
                if (b == 0x02) { i++; continue; }               // newline: no advance
                if (b == 0x00) break;
                if (MsgIsCmd(b))
                {
                    if (!MsgCmdSize.TryGetValue(b, out var n) || i + n >= end)
                    { Console.WriteLine($"  [FAIL] {tag}: bad command 0x{b:X2} in text span"); fail++; break; }
                    i += n + 1;
                    continue;
                }
                int cell = b - 0x20;
                if (cell < 0 || cell >= 280) { Console.WriteLine($"  [FAIL] {tag}: control byte 0x{b:X2} in text span"); fail++; break; }
                w += sp[cell] / 2.0;
                i++;
            }
            return w;
        }

        double MaxLineWidth(byte[] msg, int start, int end, byte[] sp, string tag)
        {
            double w = 0, max = 0;
            int i = start;
            while (i < end)
            {
                byte b = msg[i];
                if (b == 0x01) { w += 5; i++; continue; }
                if (b == 0x02) { if (w > max) max = w; w = 0; i++; continue; }
                if (b == 0x00) break;
                if (MsgIsCmd(b))
                {
                    if (!MsgCmdSize.TryGetValue(b, out var n) || i + n >= end)
                    { Console.WriteLine($"  [FAIL] {tag}: bad command 0x{b:X2} in text span"); fail++; break; }
                    i += n + 1;
                    continue;
                }
                int cell = b - 0x20;
                if (cell < 0 || cell >= 280) { Console.WriteLine($"  [FAIL] {tag}: control byte 0x{b:X2} in text span"); fail++; break; }
                w += sp[cell] / 2.0;
                i++;
            }
            return max > w ? max : w;
        }

        // --- batch rows ---
        var rows = new List<(int id, string en, string ar)>();
        foreach (var line in File.ReadLines(tsv))
        {
            if (line.Trim().Length == 0) continue;
            var p = line.Split('\t');
            if (p.Length != 3) { Console.WriteLine($"  [FAIL] bad tsv row: {line}"); fail++; continue; }
            rows.Add((int.Parse(p[0]), p[1].Replace("\\n", "\n"), p[2].Replace("\\n", "\n")));   // literal \n = newline (line-based TSV)
        }
        var batchIds = rows.Select(r => r.id).ToHashSet();
        Console.WriteLine($"batchtt: {rows.Count} rows, {batchIds.Count} unique ids from {Path.GetFileName(tsv)}");

        // --- parse original tt.bar ---
        var bar = File.ReadAllBytes(origBarPath);
        Check(bar.Length >= 48 && System.Text.Encoding.ASCII.GetString(bar, 0, 3) == "BAR",
            $"orig tt bar: BAR magic, size={bar.Length}");
        uint entryCount = BitConverter.ToUInt32(bar, 4);
        uint sysOff = BitConverter.ToUInt32(bar, 24), sysLen = BitConverter.ToUInt32(bar, 28);
        uint mdOff = BitConverter.ToUInt32(bar, 40), mdLen = BitConverter.ToUInt32(bar, 44);
        Check(entryCount == 2 && sysOff == 48 && mdLen >= 0 && mdOff == ((sysOff + sysLen + 15) & ~15u)
              && mdOff + mdLen == bar.Length,
            $"orig tt bar: entries=2 sys=({sysOff},{sysLen}) md_m=({mdOff},{mdLen}) aligned16, size={bar.Length}");
        byte[] msg0 = bar.AsSpan((int)sysOff, (int)sysLen).ToArray();

        // --- parse msg blob ---
        uint mmagic = BitConverter.ToUInt32(msg0, 0);
        uint mcount = BitConverter.ToUInt32(msg0, 4);
        Check(mmagic == 1 && mcount == MsgCount, $"msg: magic={mmagic} count={mcount} (expect 1/{MsgCount})");
        var ids = new int[mcount];
        var offs = new uint[mcount];
        for (int i = 0; i < mcount; i++)
        {
            ids[i] = (int)BitConverter.ToUInt32(msg0, 8 + i * 8);
            offs[i] = BitConverter.ToUInt32(msg0, 8 + i * 8 + 4);
        }
        bool sorted = true;
        for (int i = 1; i < mcount; i++) if (offs[i] < offs[i - 1]) { sorted = false; break; }
        Check(sorted && offs[0] == 8 + mcount * 8, $"table sorted asc, firstOff={offs[0]} (expect {8 + mcount * 8})");
        var origMsgs = new byte[mcount][];
        int badEnd = 0, interiorZero = 0;
        for (int i = 0; i < mcount; i++)
        {
            int start = (int)offs[i];
            int end = i + 1 < mcount ? (int)offs[i + 1] : (int)sysLen;
            var m = msg0.AsSpan(start, end - start).ToArray();
            origMsgs[i] = m;
            if (m.Length == 0 || m[^1] != 0x00) badEnd++;
            if (m.Take(m.Length - 1).Contains((byte)0x00)) interiorZero++;
        }
        Check(badEnd == 0, $"all {mcount} messages end with 0x00 (badEnd={badEnd})");
        Console.WriteLine($"  [INFO] {interiorZero} messages contain 0x00 before last byte (empty / interior End — skip these ids)");
        var idToIdx = new Dictionary<int, int>();
        for (int i = 0; i < mcount; i++) idToIdx[ids[i]] = i;

        // --- sp tables (shared font) ---
        var spOrig = File.ReadAllBytes(origListPath);
        var spNew = File.ReadAllBytes(newListPath);
        Check(spOrig.Length == 280 && Sha256Str(spNew) == ExpectedListSha,
            $"sys.list orig=280 bytes, out sha={Sha256Str(spNew).Substring(0, 8)}… (expect {ExpectedListSha.Substring(0, 8)}…)");

        // --- process rows: EN match + AR encode + roundtrip + widths ---
        var replaced = new Dictionary<int, byte[]>();   // id -> full new message (prefix + AR bytes + End)
        var report = new StringBuilder();
        report.AppendLine("id\ten\tar\tar_px\ten_px\tratio_pct\tstatus\ttrue_ratio_pct\tover130");
        int enMismatch = 0, rtFail = 0, encFail = 0, over = 0, over100 = 0;
        foreach (var (id, en, ar) in rows)
        {
            if (!idToIdx.TryGetValue(id, out var idx))
            { Console.WriteLine($"  [FAIL] id {id} not in msg (en={en})"); fail++; continue; }
            string status = "OK";
            var m = origMsgs[idx];
            int textStart, textEnd = m.Length - 1;               // last byte = End (0x00), verified above
            string enBack;
            try
            {
                textStart = MsgSkipLeading(m);
                enBack = MsgDecodeEn(m, textStart, textEnd, cellToChar);
            }
            catch (Exception e)
            { enMismatch++; fail++; Console.WriteLine($"  [FAIL] id {id} EN decode: {e.Message}"); continue; }
            if (enBack != en)
            { enMismatch++; fail++; status = "EN_MISMATCH"; Console.WriteLine($"  [FAIL] id {id} EN mismatch: msg=\"{enBack}\" tsv=\"{en}\""); }
            byte[] arBytes = null;
            string arNorm = ar;
            noLigNow = NoLigAll || noLigIds.Contains(id); try { arNorm = FixState(ar, m.AsSpan(0, textStart).ToArray()); arBytes = Encode(arNorm); }
            catch (Exception e) { encFail++; fail++; status = "ENC_FAIL"; Console.WriteLine($"  [FAIL] id {id} EN={en}: {e.Message}"); }
            if (arBytes != null)
            {
                try
                {
                    string rt = DecodeAr(arBytes);
                    if (rt != arNorm) { rtFail++; fail++; status = "RT_FAIL"; Console.WriteLine($"  [FAIL] id {id} roundtrip mismatch (en={en})"); }
                }
                catch (Exception e) { rtFail++; fail++; status = "RT_FAIL"; Console.WriteLine($"  [FAIL] id {id} roundtrip: {e.Message}"); }
                replaced[id] = m.Take(textStart).Concat(arBytes).Concat(new byte[] { 0x00 }).ToArray();
            }
            double arPx = arBytes != null ? Width(replaced[id], textStart, textStart + arBytes.Length, spNew, $"id {id}") : 0;
            double enPx = Width(m, textStart, textEnd, spOrig, $"id {id}");
            double ratio = enPx > 0 ? arPx / enPx * 100 : 0;
            double arMax = arBytes != null ? MaxLineWidth(replaced[id], textStart, textStart + arBytes.Length, spNew, $"id {id} line") : 0;
            double enMax = MaxLineWidth(m, textStart, textEnd, spOrig, $"id {id} line");
            double trueRatio = enMax > 0 ? arMax / enMax * 100 : 0;
            if (arBytes != null && ratio > 100) over100++;
            if (arBytes != null && ratio > 150) { over++; if (status == "OK") status = "WARN_OVER_150"; }
            report.AppendLine(string.Join("\t", id, en.Replace("\n", "\\n"), ar.Replace("\n", "\\n"),
                arPx.ToString("F1"), enPx.ToString("F1"), ratio.ToString("F0"), status,
                trueRatio.ToString("F0"), trueRatio > 130 ? "YES" : ""));
        }
        Check(enMismatch == 0, $"EN text matches original bytes for all {rows.Count} rows (bad={enMismatch})");
        Check(encFail == 0 && rtFail == 0, $"AR encode + roundtrip OK (encFail={encFail} rtFail={rtFail})");
        Check(replaced.Count == rows.Count, $"all {rows.Count} rows encoded");
        Console.WriteLine($"  [INFO] width >100% of EN: {over100} rows, >150% (WARN): {over} rows (see {Path.GetFileName(reportPath)})");

        // --- rebuild msg payload (non-batch byte-identical) ---
        var outMsgs = new byte[mcount][];
        var newOffs = new uint[mcount];
        uint run = 8 + mcount * 8;
        for (int i = 0; i < mcount; i++)
        {
            outMsgs[i] = replaced.TryGetValue(ids[i], out var nw) ? nw : origMsgs[i];
            newOffs[i] = run;
            run += (uint)outMsgs[i].Length;
        }
        var payload = new byte[run];
        BitConverter.GetBytes(1u).CopyTo(payload, 0);
        BitConverter.GetBytes(mcount).CopyTo(payload, 4);
        for (int i = 0; i < mcount; i++)
        {
            BitConverter.GetBytes((uint)ids[i]).CopyTo(payload, 8 + i * 8);
            BitConverter.GetBytes(newOffs[i]).CopyTo(payload, 8 + i * 8 + 4);
            outMsgs[i].CopyTo(payload, (int)newOffs[i]);
        }
        int nonBatchDiff = 0;
        for (int i = 0; i < mcount; i++)
            if (!batchIds.Contains(ids[i]) && !origMsgs[i].AsSpan().SequenceEqual(outMsgs[i])) nonBatchDiff++;
        Check(nonBatchDiff == 0, $"non-batch messages byte-identical to original (changed: {nonBatchDiff})");

        // --- rebuild bar file, md_m copied through byte-identically ---
        int newSysLen = payload.Length;
        int newMdOff = ((48 + newSysLen + 15) & ~15);
        var nb = new byte[newMdOff + (int)mdLen];
        Array.Copy(bar, 0, nb, 0, 48);                  // header + entry table verbatim
        BitConverter.GetBytes((uint)newSysLen).CopyTo(nb, 28);
        BitConverter.GetBytes((uint)newMdOff).CopyTo(nb, 40);
        BitConverter.GetBytes(mdLen).CopyTo(nb, 44);
        payload.CopyTo(nb, 48);
        Array.Copy(bar, (int)mdOff, nb, newMdOff, (int)mdLen);   // md_m texture verbatim
        Check(nb.Length == newMdOff + mdLen && newMdOff - 48 >= newSysLen,
            $"built tt bar: size={nb.Length} sys=(48,{newSysLen}) md_m=({newMdOff},{mdLen})");

        // --- reparse built bar independently ---
        {
            uint bCount = BitConverter.ToUInt32(nb, 4);
            uint bOff = BitConverter.ToUInt32(nb, 24), bLen = BitConverter.ToUInt32(nb, 28);
            uint bMd = BitConverter.ToUInt32(nb, 40), bMdLen = BitConverter.ToUInt32(nb, 44);
            var bp = nb.AsSpan((int)bOff, (int)bLen).ToArray();
            uint bMagic = BitConverter.ToUInt32(bp, 0);
            uint bMsgCount = BitConverter.ToUInt32(bp, 4);
            bool ok = bCount == 2 && bOff == 48 && bMagic == 1 && bMsgCount == mcount
                      && bMdLen == mdLen && bMd == (uint)newMdOff;
            int mismatch = 0;
            for (int i = 0; i < mcount && ok; i++)
            {
                int id = (int)BitConverter.ToUInt32(bp, 8 + i * 8);
                uint o = BitConverter.ToUInt32(bp, 8 + i * 8 + 4);
                uint o2 = i + 1 < mcount ? BitConverter.ToUInt32(bp, 8 + (i + 1) * 8 + 4) : bLen;
                var m = bp.AsSpan((int)o, (int)(o2 - o)).ToArray();
                byte[] want;
                if (batchIds.Contains(id))
                {
                    if (!replaced.TryGetValue(id, out want)) { mismatch++; continue; }
                }
                else want = origMsgs[Array.IndexOf(ids, id)];
                if (!m.AsSpan().SequenceEqual(want)) mismatch++;
            }
            bool mdOk = bar.AsSpan((int)mdOff, (int)mdLen).SequenceEqual(nb.AsSpan(newMdOff, (int)mdLen));
            Check(ok && mismatch == 0 && mdOk, $"built bar reparse: structure OK, message mismatch={mismatch}, md_m identical={mdOk}");
        }

        // --- report (always written; UTF-8 no BOM) ---
        Directory.CreateDirectory(Path.GetDirectoryName(reportPath));
        File.WriteAllText(reportPath, report.ToString(), new UTF8Encoding(false));
        Console.WriteLine($"wrote {reportPath}");

        if (fail > 0)
        {
            Console.WriteLine($"RESULT: {fail} FAILURES — nothing written to mod");
            return 1;
        }

        // --- write built bar, backup mod, install ---
        Directory.CreateDirectory(outDir);
        File.WriteAllBytes(outBarPath, nb);
        string builtSha = Sha256Str(nb);
        Console.WriteLine($"built {outBarPath}  size={nb.Length}  sha256={builtSha}");
        if (Environment.GetEnvironmentVariable("KH2_NO_INSTALL") == "1")   // build-only: never touch the mod, never create a backup
        { Console.WriteLine("KH2_NO_INSTALL=1: built only - mod NOT touched"); Console.WriteLine("\nRESULT: BUILD-ONLY PASS"); return 0; }

        string tsvName = Path.GetFileNameWithoutExtension(tsv);
        string digits = new string(tsvName.Where(char.IsDigit).ToArray());
        string bakPath = ModBar + ".pre-batch" + (digits.Length > 0 ? digits : "1") + ".bak";
        if (!File.Exists(bakPath))
        {
            File.Copy(ModBar, bakPath);
            Console.WriteLine($"backup created: {bakPath}");
        }
        else Console.WriteLine($"backup already exists: {bakPath}");
        var bakSha = Sha256Str(File.ReadAllBytes(bakPath));
        var curSha = Sha256Str(File.ReadAllBytes(ModBar));
        Console.WriteLine($"  [INFO] mod tt.bar before install sha256={curSha}");
        Console.WriteLine($"  [INFO] backup sha256={bakSha}");

        // non-batch must equal the backed-up mod too (mod == original outside the batch ids)
        {
            var bak = File.ReadAllBytes(bakPath);
            uint bOff = BitConverter.ToUInt32(bak, 24), bLen = BitConverter.ToUInt32(bak, 28);
            uint bMd = BitConverter.ToUInt32(bak, 40), bMdLen = BitConverter.ToUInt32(bak, 44);
            var bp = bak.AsSpan((int)bOff, (int)bLen).ToArray();
            uint bMsgCount = BitConverter.ToUInt32(bp, 4);
            int mismatch = 0;
            for (int i = 0; i < bMsgCount; i++)
            {
                int id = (int)BitConverter.ToUInt32(bp, 8 + i * 8);
                if (batchIds.Contains(id)) continue;
                uint o = BitConverter.ToUInt32(bp, 8 + i * 8 + 4);
                uint o2 = i + 1 < bMsgCount ? BitConverter.ToUInt32(bp, 8 + (i + 1) * 8 + 4) : bLen;
                var m = bp.AsSpan((int)o, (int)(o2 - o)).ToArray();
                int j = Array.IndexOf(ids, id);
                if (j < 0 || !m.AsSpan().SequenceEqual(origMsgs[j])) mismatch++;
            }
            bool mdOk = bMdLen == mdLen && bMd + bMdLen <= (uint)bak.Length
                        && bak.AsSpan((int)bMd, (int)bMdLen).SequenceEqual(bar.AsSpan((int)mdOff, (int)mdLen));
            Check(mismatch == 0 && mdOk, $"non-batch messages identical to pre-install backup (mismatch={mismatch}), md_m identical={mdOk}");
        }

        if (fail > 0)
        {
            Console.WriteLine($"RESULT: {fail} FAILURES — mod NOT modified");
            return 1;
        }

        File.WriteAllBytes(ModBar, nb);
        var instSha = Sha256Str(File.ReadAllBytes(ModBar));
        Check(instSha == builtSha, $"installed {ModBar} sha256={instSha}");

        Console.WriteLine($"\nRESULT: ALL PASS ({rows.Count} messages translated, {over} width warnings)");
        return 0;
    }

    // ================= dump original EN (token-aware) for building batch TSVs =================
    // optional bar argument for `dump` / `preflight`: null keeps the original sys.bar default
    static string ResolveBar(string barPath, string defaultRelative)
    {
        if (string.IsNullOrEmpty(barPath)) return Path.Combine(Root, defaultRelative);
        if (File.Exists(barPath)) return Path.GetFullPath(barPath);
        if (File.Exists(Path.Combine(Root, barPath))) return Path.Combine(Root, barPath);
        throw new Exception($"bar not found: {barPath}");
    }

    // ================= one-message injection (tt.bar sys-atlas experiment) =================
    // Re-encodes exactly one message in place, keeping every other message and the bar's
    // second entry (tt.bar "md_m" icon texture) byte-identical.  Nothing is written to any TSV.
    static double MsgWidth(byte[] msg, int start, int end, byte[] sp)
    {
        double w = 0; int i = start;
        while (i < end)
        {
            byte b = msg[i];
            if (b == 0x01) { w += 5; i++; continue; }
            if (b == 0x02) { i++; continue; }
            if (b == 0x00) break;
            if (MsgIsCmd(b))
            {
                if (!MsgCmdSize.TryGetValue(b, out var n) || i + n >= end) break;
                i += n + 1; continue;
            }
            int cell = b - 0x20;
            if (cell >= 0 && cell < sp.Length) w += sp[cell] / 2.0;
            i++;
        }
        return w;
    }

    static int Inject(string barPath, string idSpec, string textPath, string outPath)
    {
        int fail = 0;
        void Check(bool ok, string msg) { Console.WriteLine($"  [{(ok ? "PASS" : "FAIL")}] {msg}"); if (!ok) fail++; }

        var arabicEnc = new Dictionary<(char letter, int form), int>();
        var arabicDec = new Dictionary<int, (char letter, int form)>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\allocation.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            int c = int.Parse(p[4]);
            arabicEnc[(p[0][0], int.Parse(p[2]))] = c;
            arabicDec[c] = (p[0][0], int.Parse(p[2]));
        }
        var cellToChar = new Dictionary<int, char>();
        var charToCell = new Dictionary<char, int>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length < 11 || p[10] != "GLYPH") continue;
            int cell = int.Parse(p[1]);
            if (cell < 0 || p[5].Length != 1) continue;
            char ch = p[5][0];
            cellToChar[cell] = ch;
            if (!arabicDec.ContainsKey(cell) && !charToCell.ContainsKey(ch)) charToCell[ch] = cell;
        }

        int id = int.Parse(idSpec);
        string ar = File.ReadAllText(textPath).TrimEnd('\r', '\n');

        var bar = File.ReadAllBytes(barPath);
        uint sysOff = BitConverter.ToUInt32(bar, 24), sysLen = BitConverter.ToUInt32(bar, 28);
        uint mdOff = BitConverter.ToUInt32(bar, 40), mdLen = BitConverter.ToUInt32(bar, 44);
        var md = bar.AsSpan((int)mdOff, (int)mdLen).ToArray();
        var payload = bar.AsSpan((int)sysOff, (int)sysLen).ToArray();
        uint mcount = BitConverter.ToUInt32(payload, 4);
        var ids = new int[mcount]; var offs = new uint[mcount];
        for (int i = 0; i < mcount; i++)
        { ids[i] = (int)BitConverter.ToUInt32(payload, 8 + i * 8); offs[i] = BitConverter.ToUInt32(payload, 8 + i * 8 + 4); }
        var origMsgs = new byte[mcount][];
        for (int i = 0; i < mcount; i++)
        { int s = (int)offs[i]; int e = i + 1 < mcount ? (int)offs[i + 1] : (int)sysLen; origMsgs[i] = payload.AsSpan(s, e - s).ToArray(); }

        int idx = Array.IndexOf(ids, id);
        if (idx < 0) { Console.WriteLine($"inject: id {id} not in bar"); return 1; }
        var m = origMsgs[idx];
        int textStart; string en;
        try { textStart = MsgSkipLeading(m); en = MsgDecodeEn(m, textStart, m.Length - 1, cellToChar); }
        catch (Exception e) { Console.WriteLine($"inject: decode failed: {e.Message}"); return 1; }

        string arNorm; byte[] arBytes;
        try { arNorm = FixState(ar, m.AsSpan(0, textStart).ToArray()); arBytes = EncodeMsg(arNorm, arabicEnc, charToCell, -1, -1, AltPeriodOn ? AltPeriodCell : -1); }
        catch (Exception e) { Console.WriteLine($"inject: encode failed: {e.Message}"); return 1; }

        var newMsg = new byte[textStart + arBytes.Length + 1];
        Array.Copy(m, 0, newMsg, 0, textStart);
        Array.Copy(arBytes, 0, newMsg, textStart, arBytes.Length);

        var outMsgs = new byte[mcount][];
        var newOffs = new uint[mcount];
        uint run = 8 + mcount * 8;
        for (int i = 0; i < mcount; i++)
        { outMsgs[i] = i == idx ? newMsg : origMsgs[i]; newOffs[i] = run; run += (uint)outMsgs[i].Length; }
        var np = new byte[run];
        BitConverter.GetBytes(1u).CopyTo(np, 0);
        BitConverter.GetBytes(mcount).CopyTo(np, 4);
        for (int i = 0; i < mcount; i++)
        {
            BitConverter.GetBytes((uint)ids[i]).CopyTo(np, 8 + i * 8);
            BitConverter.GetBytes(newOffs[i]).CopyTo(np, 8 + i * 8 + 4);
            outMsgs[i].CopyTo(np, (int)newOffs[i]);
        }
        int changed = 0;
        for (int i = 0; i < mcount; i++) if (i != idx && !origMsgs[i].AsSpan().SequenceEqual(outMsgs[i])) changed++;
        Check(changed == 0, $"all {mcount - 1} non-target messages byte-identical");

        int newMdOff = ((48 + np.Length + 15) & ~15);
        var nb = new byte[newMdOff + (int)mdLen];
        Array.Copy(bar, 0, nb, 0, 48);
        BitConverter.GetBytes((uint)np.Length).CopyTo(nb, 28);
        BitConverter.GetBytes((uint)newMdOff).CopyTo(nb, 40);
        BitConverter.GetBytes(mdLen).CopyTo(nb, 44);
        np.CopyTo(nb, 48);
        Array.Copy(md, 0, nb, newMdOff, mdLen);
        Check(newMdOff - 48 >= np.Length, $"bar layout: sys=(48,{np.Length}) md_m=({newMdOff},{mdLen}) size={nb.Length} (orig {bar.Length})");

        {
            uint bOff = BitConverter.ToUInt32(nb, 24), bLen = BitConverter.ToUInt32(nb, 28);
            uint bMd = BitConverter.ToUInt32(nb, 40), bMdLen = BitConverter.ToUInt32(nb, 44);
            var bp = nb.AsSpan((int)bOff, (int)bLen).ToArray();
            bool ok = bOff == 48 && BitConverter.ToUInt32(bp, 0) == 1 && BitConverter.ToUInt32(bp, 4) == mcount
                      && bMd == (uint)newMdOff && bMdLen == mdLen;
            int mismatch = 0;
            for (int i = 0; i < mcount && ok; i++)
            {
                int bid = (int)BitConverter.ToUInt32(bp, 8 + i * 8);
                uint o = BitConverter.ToUInt32(bp, 8 + i * 8 + 4);
                uint o2 = i + 1 < mcount ? BitConverter.ToUInt32(bp, 8 + (i + 1) * 8 + 4) : bLen;
                var bm = bp.AsSpan((int)o, (int)(o2 - o)).ToArray();
                if (!bm.AsSpan().SequenceEqual(i == idx ? newMsg : origMsgs[i])) mismatch++;
            }
            bool mdOk = md.AsSpan().SequenceEqual(nb.AsSpan(newMdOff, (int)mdLen));
            Check(ok && mismatch == 0 && mdOk, $"reparse OK, msg mismatch={mismatch}, md_m identical={mdOk}");
            try
            {
                int ts = MsgSkipLeading(newMsg);
                MsgDecodeEn(newMsg, ts, newMsg.Length - 1, cellToChar);
                Check(true, "re-decode of injected message");
            }
            catch (Exception e) { Check(false, $"re-decode: {e.Message}"); }
        }

        string spOrigPath = Path.Combine(Root, @"technical\extracted\bar\us\fontinfo\sys.list");
        string spNewPath = Path.Combine(Root, @"font-rtl\arabic\out\sys.list");
        if (File.Exists(spOrigPath) && File.Exists(spNewPath))
        {
            double enPx = MsgWidth(m, textStart, m.Length - 1, File.ReadAllBytes(spOrigPath));
            double arPx = MsgWidth(newMsg, textStart, textStart + arBytes.Length, File.ReadAllBytes(spNewPath));
            Console.WriteLine($"  [INFO] width EN={enPx:F1}px  AR={arPx:F1}px  ratio={(enPx > 0 ? arPx / enPx * 100 : 0):F0}%");
        }

        Console.WriteLine($"inject: id={id}  prefixBytes={textStart}  enLen={en.Length}  arLen={arBytes.Length}");
        Console.WriteLine($"  EN: {en.Replace("\n", "\\n")}");
        Console.WriteLine($"  AR: {arNorm.Replace("\n", "\\n")}");

        if (fail > 0) { Console.WriteLine("RESULT: FAILURES — nothing written"); return 1; }
        File.WriteAllBytes(outPath, nb);
        Console.WriteLine($"wrote {outPath}");
        return 0;
    }

    static int Dump(string arg, string barPath = null)
    {
        string origBarPath = ResolveBar(barPath, @"technical\extracted\game-data\original\msg\us\sys.bar");
        var cellToChar = new Dictionary<int, char>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length < 11 || p[10] != "GLYPH") continue;
            int cell = int.Parse(p[1]);
            if (cell < 0 || p[5].Length != 1) continue;
            cellToChar[cell] = p[5][0];
        }

        var bar = File.ReadAllBytes(origBarPath);
        uint sysOff = BitConverter.ToUInt32(bar, 24), sysLen = BitConverter.ToUInt32(bar, 28);
        var msg0 = bar.AsSpan((int)sysOff, (int)sysLen).ToArray();
        uint mcount = BitConverter.ToUInt32(msg0, 4);
        var ids = new int[mcount]; var offs = new uint[mcount];
        for (int i = 0; i < mcount; i++)
        {
            ids[i] = (int)BitConverter.ToUInt32(msg0, 8 + i * 8);
            offs[i] = BitConverter.ToUInt32(msg0, 8 + i * 8 + 4);
        }
        var msgs = new Dictionary<int, byte[]>();
        for (int i = 0; i < mcount; i++)
        {
            int s = (int)offs[i];
            int e = i + 1 < mcount ? (int)offs[i + 1] : (int)sysLen;
            msgs[ids[i]] = msg0.AsSpan(s, e - s).ToArray();
        }

        var idList = new List<int>();
        if (string.IsNullOrEmpty(arg)) { Console.WriteLine("usage: dump <id1,id2,...|file|START-END>"); return 1; }
        if (File.Exists(arg))
        {
            foreach (var l in File.ReadAllLines(arg))
                if (l.Trim().Length > 0) idList.Add(int.Parse(l.Trim()));
        }
        else if (arg.Contains('-') && !arg.StartsWith("-"))
        {
            var pp = arg.Split('-');
            for (int i = int.Parse(pp[0]); i <= int.Parse(pp[1]); i++) idList.Add(i);
        }
        else foreach (var x in arg.Split(',')) idList.Add(int.Parse(x.Trim()));

        int errs = 0;
        var outSb = new StringBuilder();
        foreach (var id in idList)
        {
            if (!msgs.TryGetValue(id, out var m)) { outSb.Append($"{id}\t#NO_ID\n"); errs++; continue; }
            if (m.All(x => x == 0x00)) { outSb.Append($"{id}\t#EMPTY\n"); continue; }   // empty message (End + padding): nothing to translate, not an error
            try
            {
                int ts = MsgSkipLeading(m);
                string txt = MsgDecodeEn(m, ts, m.Length - 1, cellToChar).Replace("\n", "\\n");
                outSb.Append($"{id}\t{txt}\n");
            }
            catch (Exception e) { outSb.Append($"{id}\t#ERROR\t{e.Message}\n"); errs++; }
        }
        Console.Out.Write(outSb.ToString());
        Console.Error.WriteLine($"dump: {idList.Count} ids, {errs} errors");
        return errs > 0 ? 1 : 0;
    }

    static Dictionary<int, char> LoadCellToChar()
    {
        var cellToChar = new Dictionary<int, char>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length < 11 || p[10] != "GLYPH") continue;
            int cell = int.Parse(p[1]);
            if (cell < 0 || p[5].Length != 1) continue;
            cellToChar[cell] = p[5][0];
        }
        return cellToChar;
    }

    static int BarDump(string path)
    {
        if (string.IsNullOrEmpty(path)) { Console.WriteLine("usage: bardump <file.bar>"); return 1; }
        if (!File.Exists(path)) { Console.WriteLine($"bardump: not found {path}"); return 1; }
        var cellToChar = LoadCellToChar();
        var entries = P.BarEntries(path);
        if (Environment.GetEnvironmentVariable("BAROUT") is string outDir && outDir.Length > 0)
        {
            Directory.CreateDirectory(outDir);
            for (int i = 0; i < entries.Count; i++)
                File.WriteAllBytes(Path.Combine(outDir, $"{i}_{entries[i].name}.bin"), entries[i].data);
        }
        int msgEntries = 0, totalMsgs = 0, errs = 0;
        var outSb = new StringBuilder();
        for (int ei = 0; ei < entries.Count; ei++)
        {
            var (name, d) = entries[ei];
            Console.Error.WriteLine($"  entry[{ei}] '{name}' {d.Length} bytes");
            if (d.Length < 16) continue;
            uint mc = BitConverter.ToUInt32(d, 4);
            if (mc == 0 || mc > 1000000 || 8L + (long)mc * 8 > d.Length) continue;
            msgEntries++; outSb.Append($"# entry {ei} '{name}' messages={mc}\n");
            var msg0 = d;
            for (int i = 0; i < mc; i++)
            {
                int id = (int)BitConverter.ToUInt32(msg0, 8 + i * 8);
                int s = (int)BitConverter.ToUInt32(msg0, 8 + i * 8 + 4);
                int e = i + 1 < mc ? (int)BitConverter.ToUInt32(msg0, 8 + (i + 1) * 8 + 4) : (int)d.Length;
                if (s < 0 || e > d.Length || s >= e) { outSb.Append($"{id}\t#BAD_RANGE {s}-{e}\n"); errs++; continue; }
                var m = msg0.AsSpan(s, e - s).ToArray();
                totalMsgs++;
                try
                {
                    string rtxt = RenderMsg(m, cellToChar).Replace("\n", "\\n");
                    outSb.Append($"{id}\t{rtxt}\n");
                }
                catch (Exception ex) { outSb.Append($"{id}\t#ERROR\t{ex.Message}\n"); errs++; }
            }
        }
        if (msgEntries == 0) { Console.Error.WriteLine("bardump: no msg entry found"); return 2; }
        Console.Out.Write(outSb.ToString());
        Console.Error.WriteLine($"bardump: {msgEntries} msg entries, {totalMsgs} msgs, {errs} errors");
        return 0;
    }

    static string RenderMsg(byte[] m, Dictionary<int, char> cellToChar)
    {
        var list = (System.Collections.IEnumerable)P.DecodeM.Invoke(P.Enc, new object[] { m });
        var sb = new StringBuilder();
        foreach (object o in list)
        {
            var t = o.GetType();
            int cmd = (int)t.GetProperty("Command").GetValue(o);
            var data = (byte[])t.GetProperty("Data").GetValue(o);
            string txt = (string)t.GetProperty("Text").GetValue(o);
            if (cmd == 0) break;                                  // End
            if (cmd == 1) { sb.Append(string.IsNullOrEmpty(txt) ? " " : txt); continue; }
            if (cmd == 2) { sb.Append(string.IsNullOrEmpty(txt) ? "\n" : txt); continue; }
            sb.Append($"<{cmd:X2}");
            if (data != null && data.Length > 0) sb.Append(" " + BitConverter.ToString(data).Replace("-", " "));
            sb.Append(">");
        }
        return sb.ToString();
    }

    // ================= metrics probe: choose font/size/baseline/scaleX =================
    static int Probe()
    {
        string[] fonts = { "Sakkal Majalla", "Arabic Typesetting", "Traditional Arabic", "Simplified Arabic", "Simplified Arabic Fixed",
                           "Arial", "Tahoma", "Segoe UI", "Times New Roman", "Calibri", "MV Boli", "Urdu Typesetting",
                           "Aldhabi", "Andalus", "Leelawadee UI", "Courier New", "Microsoft Uighur" };
        int[] sizes = { 11, 12, 13, 14, 15, 16, 17, 18, 20, 22 };

        Console.WriteLine("target: baseline<=20 (Latin=20), ascTop>=7 (Latin cap top=7), desc bottom<=23, inkW<=9");
        Console.WriteLine("\nfont                 sz  maxAsc maxDesc maxW  kX    base top bot  fits@base20   w<=9 w10-12 w13-15 w>=16 perGlyphKX");
        var best = new List<(string font, int sz, double score, int baseline, float kx, int asc, int desc, int w)>();

        foreach (var fn in fonts)
        foreach (int sz in sizes)
        {
            using var f = new Font(fn, sz, FontStyle.Regular, GraphicsUnit.Pixel);

            // baseline reference = bottom of isolated alef (it sits on the baseline)
            var (bl, _) = RenderBox("ا", f, 1f);
            if (bl < 0) continue;
            int baseline = bl;

            int maxAsc = 0, maxDesc = 0, maxW = 0;
            int w9 = 0, w12 = 0, w15 = 0, w16 = 0;
            double kxSum = 0; int kxN = 0, kxSqueeze = 0;
            foreach (var (letter, form) in Ar.Needed())
            {
                int cp = Ar.Pf[letter][form];
                var (b2, box) = RenderBox(((char)cp).ToString(), f, 1f);
                if (b2 < 0) { Console.WriteLine($"  !! no ink for U+{cp:X4} {letter} form{form} @ {fn} {sz}"); continue; }
                maxAsc = Math.Max(maxAsc, baseline - box.t);
                maxDesc = Math.Max(maxDesc, box.b - baseline);
                int w = box.r - box.l + 1;
                maxW = Math.Max(maxW, w);
                if (w <= 9) w9++; else if (w <= 12) w12++; else if (w <= 15) w15++; else w16++;
                double k = w > 9 ? 9.0 / w : 1.0;
                kxSum += k; kxN++;
                if (k < 1.0) kxSqueeze++;
            }
            double kx = maxW > CW ? (double)CW / maxW : 1.0;
            double kxAvg = kxN > 0 ? kxSum / kxN : 1;
            int base20 = 20;
            int top = base20 - maxAsc, bot = base20 + maxDesc;
            bool fits20 = top >= 0 && bot <= CH - 1 && maxW * kx <= CW + 0.01;
            // best baseline we can use
            int baseOk = Math.Min(20, CH - 1 - maxDesc);
            int topOk = baseOk - maxAsc, botOk = baseOk + maxDesc;
            bool fits = topOk >= 0 && botOk <= CH - 1;
            Console.WriteLine($"{fn,-20} {sz,2}  {maxAsc,6} {maxDesc,7} {maxW,5}  {kx:F2}  {baseOk,4} {topOk,3} {botOk,3}   {(fits20 ? "YES" : (fits ? "base" + baseOk : "NO")),-10} {w9,4} {w12,6} {w15,6} {w16,6}  {kxAvg:F2}/{kxSqueeze}sq");
            if (fits)
                best.Add((fn, sz, 0, baseOk, (float)kx, maxAsc, maxDesc, maxW));
        }

        Console.WriteLine("\n== ranked: prefer baseline==20, then max alef height (maxAsc), then max kX ==");
        foreach (var b in best.OrderByDescending(x => x.baseline == 20).ThenByDescending(x => x.asc).ThenByDescending(x => x.kx).Take(14))
            Console.WriteLine($"  {b.font,-20} {b.sz,2}px  baseline={b.baseline} asc={b.asc} desc={b.desc} maxW={b.w} kX={b.kx:F2} alefH={b.asc + 1}");

        return 0;
    }

    /// <summary>Render one string; returns (baselineY, inkBox) or (-1, default) when empty.</summary>
    static (int baseline, (int l, int r, int t, int b)) RenderBox(string text, Font f, float scaleX)    {
        const int W = 512, H = 256;
        using var b = new Bitmap(W, H, PixelFormat.Format32bppArgb);
        using (var g = Graphics.FromImage(b))
        {
            g.Clear(Color.Black);
            g.TextRenderingHint = TextRenderingHint.SingleBitPerPixelGridFit;
            g.SmoothingMode = SmoothingMode.None;
            g.PixelOffsetMode = PixelOffsetMode.Half;
            if (scaleX != 1f) g.Transform = new Matrix(scaleX, 0, 0, 1, 0, 0);
            var sf = (StringFormat)StringFormat.GenericTypographic.Clone();
            sf.Alignment = StringAlignment.Near; sf.LineAlignment = StringAlignment.Near;
            g.DrawString(text, f, Brushes.White, new RectangleF(0, 0, W / Math.Max(scaleX, 0.01f), H), sf);
        }
        var (l0, r0, t0, b0) = InkBox(b);
        if (r0 < 0) return (-1, default);
        return (b0, (l0, r0, t0, b0));
    }

    /// <summary>Ink bounding box via LockBits (fast). Returns (0,-1,0,-1) when empty.</summary>
    static (int l, int r, int t, int b) InkBox(Bitmap bmp, int threshold = 60)
    {
        var rect = new Rectangle(0, 0, bmp.Width, bmp.Height);
        var bd = bmp.LockBits(rect, ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
        try
        {
            int W = bmp.Width, H = bmp.Height;
            var buf = new byte[Math.Abs(bd.Stride) * H];
            Marshal.Copy(bd.Scan0, buf, 0, buf.Length);
            int l = int.MaxValue, r = -1, t = int.MaxValue, bb = -1;
            for (int y = 0; y < H; y++)
            {
                int row = y * bd.Stride;
                for (int x = 0; x < W; x++)
                    if (buf[row + x * 4 + 2] > threshold)   // BGRA -> R
                    { if (x < l) l = x; if (x > r) r = x; if (y < t) t = y; if (y > bb) bb = y; }
            }
            if (r < 0) return (0, -1, 0, -1);
            return (l, r, t, bb);
        }
        finally { bmp.UnlockBits(bd); }
    }

    // ================= visual preview: compose candidates like the engine will =================
    static (int l, int r, int t, int b) CellBox(byte[] rgb, int cell)
    {
        int x0 = (cell % COLS) * CW, y0 = (cell / COLS) * CH;
        int l = int.MaxValue, r = -1, t = int.MaxValue, b = -1;
        for (int y = 0; y < CH; y++)
            for (int x = 0; x < CW; x++)
                if (rgb[(y0 + y) * 256 + (x0 + x)] != 0)
                { if (x < l) l = x; if (x > r) r = x; if (y < t) t = y; if (y > b) b = y; }
        if (r < 0) return (0, -1, 0, -1);
        return (l, r, t, b);
    }

    /// <summary>Shape logical Arabic string; per entry: (char, form, joinsPrev). form=-1 for non-Arabic.</summary>
    static List<(char c, int form, bool jp)> Shape(string s)
    {
        var res = new List<(char, int, bool)>();
        for (int i = 0; i < s.Length; i++)
        {
            char c = s[i];
            if (!Ar.IsArabic(c)) { res.Add((c, -1, false)); continue; }
            bool jp = i > 0 && Ar.IsArabic(s[i - 1]) && Ar.JoinsNext(s[i - 1]) && Ar.JoinsPrev(c);
            bool jn = i + 1 < s.Length && Ar.IsArabic(s[i + 1]) && Ar.JoinsPrev(s[i + 1]) && Ar.JoinsNext(c);
            res.Add((c, Ar.Form(c, jp, jn), jp));
        }
        return res;
    }

    /// <summary>Render one presentation-form char at scaleX; returns cropped bitmap + ink box.</summary>
    static (Bitmap bmp, int l, int r, int t, int b) RenderGlyph(int cp, Font f, float kx)
    {
        const int W = 128, H = 64;
        var full = new Bitmap(W, H, PixelFormat.Format32bppArgb);
        using (var g = Graphics.FromImage(full))
        {
            g.Clear(Color.Black);
            g.TextRenderingHint = TextRenderingHint.SingleBitPerPixelGridFit;
            g.SmoothingMode = SmoothingMode.None;
            g.PixelOffsetMode = PixelOffsetMode.Half;
            if (kx != 1f) g.Transform = new Matrix(kx, 0, 0, 1, 0, 0);
            var sf = (StringFormat)StringFormat.GenericTypographic.Clone();
            sf.Alignment = StringAlignment.Near; sf.LineAlignment = StringAlignment.Near;
            g.DrawString(GlyphChar(cp).ToString(), f, Brushes.White,
                new RectangleF(0, 0, kx != 1f ? W / kx : W, H), sf);
        }
        var (l, r, t, b) = InkBox(full);
        if (r < 0) { full.Dispose(); return (null, 0, -1, 0, -1); }
        var crop = full.Clone(new Rectangle(l, t, r - l + 1, b - t + 1), PixelFormat.Format32bppArgb);
        full.Dispose();
        return (crop, l, r, t, b);
    }

    /// <summary>Logical shaped items → visual L→R order (RTL base), <b>per line</b>:
    /// '\n' is a hard line break and lines are NEVER reordered (engine draws line 0 first);
    /// inside a line reverse run order, reverse Arabic runs internally, keep non-Arabic runs
    /// (digits/latin/space) as-is.  A line with no Arabic is left untouched — engine draws
    /// Latin logical L→R, so its words must not be run-reversed.</summary>
    static List<(char c, int form, bool jp)> ToVisual(List<(char c, int form, bool jp)> shaped, HashSet<char> hard = null)
        => ToVisualOrder(shaped, hard).Select(k => shaped[k]).ToList();

    // Page-structure commands (Clear / Delay / DelayAndFade) end a displayed page: what follows is shown
    // later, in stored order.  They are HARD segment boundaries for RTL run reversal, exactly like '\n':
    // runs are reversed only inside a segment and the command stays at its logical position.  Inline
    // commands (colour/size state, PrintIcon, ...) are NOT boundaries - FixState relies on RTL order
    // running across them.  KH2_BOUNDARY=all (diagnostics only) makes every <C ..> command a boundary.
    static readonly byte[] BoundaryCodes = { 0x10, 0x14, 0x17 };
    static readonly bool BoundaryAll = Environment.GetEnvironmentVariable("KH2_BOUNDARY") == "all";
    static readonly bool BoundaryOff = Environment.GetEnvironmentVariable("KH2_BOUNDARY") == "off";   // = pre-fix behaviour (diagnostics)
    static bool IsBoundaryCode(byte[] raw) =>
        !BoundaryOff && raw != null && raw.Length > 0 && raw[0] < 0x20 && (BoundaryAll || Array.IndexOf(BoundaryCodes, raw[0]) >= 0);
    // Hard-boundary set that also carries the PrintIcon (cmd 0x09) sentinels.  Icons are neutral items that must
    // reverse WITH the sentence: "<icon>." (icon then full stop, logical) has to be shown as ". <icon>" in the RTL
    // line.  A plain neutral run would keep them in logical order and leave the full stop on the wrong side of
    // the icon.  Consecutive icons stay one run (button combos keep their left-to-right order).  KH2_ICONFIX=0 = old.
    sealed class HardIcons : HashSet<char> { public readonly HashSet<char> Icons = new(); }
    static readonly bool NoLigAll = Environment.GetEnvironmentVariable("KH2_NOLIGA_ALL") == "1";   // diagnostics/candidate B: plain lam+alef for every tt id
    // sys cell 46 (retail U+3002, never used in US text) is re-purposed as a tight full stop for "<.><icon>" (RTL: period AFTER the icon):
    // same glyph as cell 47 but advance 3 px, so the period ends flush with the icon cell.  KH2_PERIODFIX=0 disables.
    const int AltPeriodCell = 46;
    static readonly bool AltPeriodOn = Environment.GetEnvironmentVariable("KH2_PERIODFIX") != "0";
    static readonly bool IconFixOn = Environment.GetEnvironmentVariable("KH2_ICONFIX") != "0";
    static HashSet<char> HardOfMap(Dictionary<char, byte[]> cmdMap)
    {
        var h = new HardIcons();
        foreach (var kv in cmdMap)
        {
            if (IsBoundaryCode(kv.Value)) h.Add(kv.Key);
            if (IconFixOn && kv.Value != null && kv.Value.Length > 0 && kv.Value[0] == 0x09) h.Icons.Add(kv.Key);
        }
        return h;
    }
    static HashSet<char> HardSet(List<byte[]> raws)
    {
        var h = new HardIcons();
        for (int k = 0; k < raws.Count; k++)
        {
            if (IsBoundaryCode(raws[k])) h.Add((char)(0xE000 + k));
            if (IconFixOn && raws[k] != null && raws[k].Length > 0 && raws[k][0] == 0x09) h.Icons.Add((char)(0xE000 + k));
        }
        return h;
    }

    /// <summary>Permutation of <paramref name="s"/> performed by <see cref="ToVisual"/>:
    /// result[p] = logical index of the item shown at visual position p.
    /// <paramref name="hard"/> = sentinel chars that are hard boundaries (like '\n') but stay in place.</summary>
    static List<int> ToVisualOrder(List<(char c, int form, bool jp)> s, HashSet<char> hard = null)
    {
        var res = new List<int>(s.Count);
        var seg = new List<int>();
        var icons = (hard as HardIcons)?.Icons;
        for (int i = 0; i < s.Count; i++)
        {
            if (s[i].c == '\n' || (hard != null && hard.Contains(s[i].c)))
            { res.AddRange(ReverseRunOrder(s, seg, icons)); res.Add(i); seg = new List<int>(); }
            else seg.Add(i);
        }
        res.AddRange(ReverseRunOrder(s, seg, icons));
        return res;
    }

    static List<int> ReverseRunOrder(List<(char c, int form, bool jp)> s, List<int> seg, HashSet<char> icons = null)
    {
        if (!seg.Any(k => s[k].form >= 0)) return seg;        // no Arabic in this line → unchanged
        var runs = new List<List<int>>();
        foreach (var k in seg)
        {
            bool isAr = s[k].form >= 0;
            bool isSep = s[k].c is ' ' or '\n';               // neutrals isolated: otherwise a space
            bool prevSep = runs.Count > 0 && s[runs[^1][0]].c is ' ' or '\n';  // before Latin stays with
            bool isIcon = icons != null && icons.Count > 0 && icons.Contains(s[k].c);
            bool prevIcon = icons != null && icons.Count > 0 && runs.Count > 0 && icons.Contains(s[runs[^1][0]].c);
            if (runs.Count == 0 || isSep || prevSep           // that Latin run (never reversed) -> wrong side
                || isIcon != prevIcon                          // icon runs are separate from punctuation/Latin/digits
                || (s[runs[^1][0]].form >= 0) != isAr) runs.Add(new List<int>());
            runs[^1].Add(k);
        }
        var vis = new List<int>();
        for (int i = runs.Count - 1; i >= 0; i--)
        {
            if (s[runs[i][0]].form >= 0) runs[i].Reverse();
            vis.AddRange(runs[i]);
        }
        return vis;
    }

    /// <summary>logical string → engine bytes (ToVisual inside); shared by Batch and rt.</summary>
    static byte[] EncodeMsg(string s, Dictionary<(char letter, int form), int> arabicEnc,
                            Dictionary<char, int> charToCell, int ligCell = -1, int ligFin = -1, int altPeriod = -1)
    {
        var res = new List<byte>();
        var sent = new List<byte[]>();                       // U+E000+k -> raw command bytes
        var flat = new StringBuilder();
        int i = 0;
        while (i < s.Length)
        {
            if (s[i] == '<' && MsgTryToken(s, i, out var tl, out var raw))
            { flat.Append((char)(0xE000 + sent.Count)); sent.Add(raw); i += tl; }
            else if (s[i] == '<' && MsgTryCellToken(s, i, out var cl, out var cello))
            { flat.Append((char)(0xE000 + sent.Count)); sent.Add(new byte[] { (byte)(cello + 0x20) }); i += cl; }
            else { flat.Append(s[i]); i++; }
        }
        var visual = ToVisual(Shape(flat.ToString()), HardSet(sent));
        for (int vi = 0; vi < visual.Count; vi++)
        {
            var (c, form, _) = visual[vi];
            // lam-alef ligature (tt/evt only): visual [alef FIN][lam INI] = logical lam(not joined to its predecessor)+alef.
            // lam MED (joined from the previous letter) would need the final-form ligature (no cell) and stays two glyphs.
            if (ligCell >= 0 && c == '\u0627' && form == Ar.FIN && vi + 1 < visual.Count
                && visual[vi + 1].c == '\u0644' && visual[vi + 1].form == Ar.INI)
            { res.Add((byte)(ligCell + 0x20)); vi++; continue; }
            // final-form lam-alef (lam joined from the previous letter = MED, + alef FIN): U+FEFC cell (lamalef2 only)
            if (ligFin >= 0 && c == '\u0627' && form == Ar.FIN && vi + 1 < visual.Count
                && visual[vi + 1].c == '\u0644' && visual[vi + 1].form == Ar.MED)
            { res.Add((byte)(ligFin + 0x20)); vi++; continue; }
            if (c >= 0xE000 && c <= 0xF8FF)
            {
                int k = c - 0xE000;
                if (k >= sent.Count) throw new Exception("orphan token sentinel");
                res.AddRange(sent[k]);
                continue;
            }
            if (form >= 0)
            {
                if (!arabicEnc.TryGetValue((c, form), out var cell))
                    throw new Exception($"no allocated glyph for '{c}' form {form} (U+{(int)c:X4})");
                res.Add((byte)(cell + 0x20));
            }
            else if (c == ' ') res.Add(0x01);
            else if (c == '\n') res.Add(0x02);
            else if (altPeriod >= 0 && c == '.' && vi + 1 < visual.Count && visual[vi + 1].c >= 0xE000 && visual[vi + 1].c <= 0xF8FF
                     && visual[vi + 1].c - 0xE000 < sent.Count && sent[visual[vi + 1].c - 0xE000].Length > 0 && sent[visual[vi + 1].c - 0xE000][0] == 0x09)
                res.Add((byte)(altPeriod + 0x20));     // "." drawn right before a PrintIcon (RTL: after it): tight cell
            else
            {
                if (!charToCell.TryGetValue(c, out var cell))
                    throw new Exception($"no safe cell for U+{(int)c:X4} '{c}'");
                res.Add((byte)(cell + 0x20));
            }
        }
        return res.ToArray();
    }

    // ================= state commands (Color / TextWidth / TextScale / … + Reset) ================
    // The engine draws the byte stream L→R but reads RTL, so a state command's natural (EN/logical)
    // position is on the opposite side of its span: a plain ToVisual would emit every opener AFTER
    // its span and every Reset BEFORE it → the wrong words get coloured.  FixState returns the
    // logical string whose ToVisual emits a freshly generated command exactly where drawing needs
    // it, and by construction the state read while drawing equals the state in reading order.
    static readonly byte[] StateOpenCodes = { 0x04, 0x07, 0x0A, 0x0B, 0x0C, 0x11 };
    static bool IsStateOpenerCode(byte c) => Array.IndexOf(StateOpenCodes, c) >= 0;
    static bool IsStateCloserCode(byte c) => c == 0x03;

    static void ApplyStateCmd(Dictionary<byte, byte[]> st, byte[] raw)
    {
        if (raw.Length == 0) return;
        if (raw[0] == 0x03) { st.Clear(); return; }
        var op = new byte[raw.Length - 1];
        Array.Copy(raw, 1, op, 0, op.Length);
        st[raw[0]] = op;
    }

    static string StateSig(Dictionary<byte, byte[]> st) => st.Count == 0 ? ""
        : string.Join(",", st.OrderBy(kv => kv.Key).Select(kv => $"{kv.Key:X2}={Convert.ToHexString(kv.Value)}"));

    /// <summary>natural AR → RTL-logical AR (identity when the text has no state commands).</summary>
    static string FixState(string ar, byte[] prefix = null)
    {
        var raws = new List<byte[]>();
        var parts = new List<string>();
        var flat = new StringBuilder();
        int i = 0;
        while (i < ar.Length)
        {
            if (ar[i] == '<' && MsgTryToken(ar, i, out var tl, out var raw))
            { flat.Append((char)(0xE000 + raws.Count)); raws.Add(raw); parts.Add(ar.Substring(i, tl)); i += tl; }
            else if (ar[i] == '<' && MsgTryCellToken(ar, i, out var cl, out var cell))
            { flat.Append((char)(0xE000 + raws.Count)); raws.Add(new byte[] { (byte)(cell + 0x20) }); parts.Add(ar.Substring(i, cl)); i += cl; }
            else { flat.Append(ar[i]); parts.Add(ar[i].ToString()); i++; }
        }

        var logical = Shape(flat.ToString());
        int n = logical.Count;
        if (n == 0) return ar;

        var isOpener = new bool[n];
        var isCloser = new bool[n];
        for (int k = 0; k < n; k++)
        {
            char c = logical[k].c;
            if (c < 0xE000 || c > 0xF8FF) continue;
            var r = raws[c - 0xE000];
            if (r.Length == 0 || r[0] >= 0x20) continue;            // <X nn> cell → content, not a command
            if (IsStateCloserCode(r[0])) isCloser[k] = true;
            else if (IsStateOpenerCode(r[0])) isOpener[k] = true;   // PrintIcon/Delay/Clear stay neutral
        }
        bool anyState = false;
        for (int k = 0; k < n; k++) if (isOpener[k] || isCloser[k]) { anyState = true; break; }
        if (!anyState) return ar;                                   // batches 1-18 have none → byte-identical

        // ---- reading-order state for every item (the preserved message prefix's state applies first) ----
        var stateRaw = new Dictionary<string, byte[]>();       // every state-opener we may re-emit, by bytes
        for (int k = 0; k < n; k++)
            if (isOpener[k]) { var r = raws[logical[k].c - 0xE000]; stateRaw[Convert.ToHexString(r)] = r; }

        var prefixOpen = new List<byte[]>();
        if (prefix != null)
            for (int j = 0; j < prefix.Length && MsgIsCmd(prefix[j]);)
            {
                if (!MsgCmdSize.TryGetValue(prefix[j], out var psz)) break;
                var praw = prefix.AsSpan(j, 1 + psz).ToArray();
                if (IsStateOpenerCode(prefix[j])) { prefixOpen.Add(praw); stateRaw[Convert.ToHexString(praw)] = praw; }
                j += 1 + psz;
            }

        var st = new Dictionary<byte, byte[]>();
        foreach (var praw in prefixOpen) ApplyStateCmd(st, praw);
        var prefixState = new Dictionary<byte, byte[]>(st);    // snapshot: st is mutated while walking below
        var wantSig = new string[n];
        var wantSt = new Dictionary<byte, byte[]>[n];
        for (int k = 0; k < n; k++)
        {
            if (isOpener[k] || isCloser[k]) ApplyStateCmd(st, raws[logical[k].c - 0xE000]);
            else { wantSig[k] = StateSig(st); wantSt[k] = new Dictionary<byte, byte[]>(st); }
        }

        var contentOrder = ToVisualOrder(logical, HardSet(raws)).Where(k => !isOpener[k] && !isCloser[k]).ToArray();
        if (contentOrder.Length == 0) return ar;

        // ---- walk the DRAWING order: emit each item plus the state it must be drawn with ----
        // original state tokens are NOT copied through — they are regenerated exactly where RTL
        // needs them, which is the only placement that can be right for every layout.
        var desParts = new List<string>(contentOrder.Length);
        var desFlat = new StringBuilder();
        void EmitPart(string text, char flatTok) { desParts.Add(text); desFlat.Append(flatTok); }
        void EmitCmd(byte[] raw)
        {
            int idx = raws.Count;
            raws.Add(raw);
            string tok = MsgCmdToken(raw, 0);
            parts.Add(tok);
            EmitPart(tok, (char)(0xE000 + idx));
        }

        var cur = new Dictionary<byte, byte[]>(prefixState);    // drawing begins at the prefix state
        foreach (int k in contentOrder)
        {
            var w = wantSt[k];
            if (StateSig(cur) != wantSig[k])
            {
                if (cur.Keys.Any(c2 => !w.ContainsKey(c2))) { EmitCmd(new byte[] { 0x03 }); cur.Clear(); }
                foreach (var c2 in w.Keys.OrderBy(x => x))
                    if (!cur.ContainsKey(c2) || !cur[c2].SequenceEqual(w[c2]))
                    {
                        var wantRaw = new byte[w[c2].Length + 1];
                        wantRaw[0] = c2;
                        Array.Copy(w[c2], 0, wantRaw, 1, w[c2].Length);
                        if (!stateRaw.TryGetValue(Convert.ToHexString(wantRaw), out var raw))
                            throw new Exception($"no stored command bytes for state {Convert.ToHexString(wantRaw)}");
                        EmitCmd(raw);
                        cur[c2] = w[c2];
                    }
            }
            EmitPart(parts[k], logical[k].c);
        }

        // ---- back to a string: ToVisual(desired) so Encode reproduces exactly that byte order ----
        var desItems = Shape(desFlat.ToString());
        var back = ToVisualOrder(desItems, HardSet(raws));
        var sbOut = new StringBuilder();
        foreach (int p in back) sbOut.Append(desParts[p]);
        return sbOut.ToString();
    }

    // preflight <tsv> — run FixState over the EN (structural stand-in for the AR column)
    // to list ids whose state-command layout cannot be placed in RTL before we translate them.
    static readonly string[] StateTokPrefixes =
        { "<C 03", "<C 04", "<C 07", "<C 0A", "<C 0B", "<C 0C", "<C 11" };
    static int PreFlight(string tsvPath, string barPath = null)
    {
        if (tsvPath == null || !File.Exists(tsvPath)) { Console.WriteLine("pre: need an existing tsv"); return 1; }

        // load the pristine bar so each row sees the same leading-command prefix Batch will keep
        string origBarPath = ResolveBar(barPath, @"technical\extracted\game-data\original\msg\us\sys.bar");
        var bar = File.ReadAllBytes(origBarPath);
        uint sysOff = BitConverter.ToUInt32(bar, 24), sysLen = BitConverter.ToUInt32(bar, 28);
        var msg0 = bar.AsSpan((int)sysOff, (int)sysLen).ToArray();
        uint mcount = BitConverter.ToUInt32(msg0, 4);
        var ids = new int[mcount]; var msgs = new byte[mcount][];
        for (int i = 0; i < mcount; i++) ids[i] = (int)BitConverter.ToUInt32(msg0, 8 + i * 8);
        for (int i = 0; i < mcount; i++)
        {
            int s = (int)BitConverter.ToUInt32(msg0, 8 + i * 8 + 4);
            int e = i + 1 < mcount ? (int)BitConverter.ToUInt32(msg0, 8 + i * 8 + 12) : (int)sysLen;
            msgs[i] = msg0.AsSpan(s, e - s).ToArray();
        }
        var idToIdx = new Dictionary<int, int>();
        for (int i = 0; i < mcount; i++) idToIdx[ids[i]] = i;

        var lines = File.ReadAllLines(tsvPath, Encoding.UTF8);
        int total = 0, hasState = 0, ok = 0, fail = 0, noMsg = 0;
        var fails = new List<string>();
        for (int i = 0; i < lines.Length; i++)   // header-tolerant: a non-numeric first cell is skipped
        {
            if (string.IsNullOrWhiteSpace(lines[i])) continue;
            var p = lines[i].Split('\t');
            if (p.Length < 2 || !int.TryParse(p[0], out var id)) continue;
            total++;
            bool state = StateTokPrefixes.Any(t => p[1].Contains(t));
            if (state) hasState++;
            if (!idToIdx.TryGetValue(id, out var idx)) { noMsg++; continue; }
            try { FixState(p[1], msgs[idx].AsSpan(0, MsgSkipLeading(msgs[idx])).ToArray()); ok++; }
            catch (Exception e) { fail++; fails.Add($"{id}\t{e.Message}"); }
        }
        Console.WriteLine($"preflight: {tsvPath}");
        Console.WriteLine($"  rows={total}  has-state-cmd={hasState}  not-in-msg={noMsg}  FixState OK={ok}  INFEASIBLE={fail}");
        foreach (var f in fails) Console.WriteLine($"  [STATE] {f}");
        Console.WriteLine(fail == 0 ? "RESULT: all ids placeable" : $"RESULT: {fail} id(s) must be skipped or translated without state cmds");
        return fail == 0 ? 0 : 1;
    }

    /// <summary>
    /// Draw visual-order items L→R into target starting at startX; returns end pen X.
    /// Arabic: ink left-aligned, advance = w + (joinsPrev ? -1 : 2)  [sp = 2w+(ISO/INI?4:-2), see §3 decision];
    /// original cells: natural l, advance = sp/2.
    /// keepShift: move kept-cell ink UP by N px (simulates aligning kept baseline 20 to Arabic baseY).</summary>
    static float ComposeVisual(List<(char c, int form, bool jp)> vis, Bitmap target,
        byte[] rgb, byte[] spacing, Dictionary<char, int> charCell,
        Dictionary<(char, int), (Bitmap bmp, int t, int w)> glyphs,
        int baseY, int bl, float startX, int keepShift = 0)
    {
        float pen = startX;
        foreach (var (c, form, jp) in vis)
        {
            if (form >= 0 && glyphs.TryGetValue((c, form), out var g) && g.bmp != null)
            {
                int x = (int)Math.Round(pen);
                int y = baseY + (g.t - bl);
                using var gr = Graphics.FromImage(target);
                gr.DrawImage(g.bmp, x, y);
                pen += g.w + (jp ? -1 : 2);
            }
            else if (c == ' ') pen += 5;
            else if (charCell.TryGetValue(c, out var cell))
            {
                int x = (int)Math.Round(pen);
                int x0 = (cell % COLS) * CW, y0 = (cell / COLS) * CH;
                for (int yy = 0; yy < CH; yy++)
                {
                    int ty = yy - keepShift;
                    if (ty < 0 || ty >= target.Height) continue;
                    for (int xx = 0; xx < CW; xx++)
                    {
                        int tx = x + xx;
                        if (tx < 0 || tx >= target.Width) continue;
                        if (rgb[(y0 + yy) * 256 + (x0 + xx)] != 0)
                            target.SetPixel(tx, ty, Color.White);
                    }
                }
                pen += spacing[cell] / 2f;
            }
            else pen += 5;
        }
        return pen;
    }

    static int Preview()
    {
        var rgb = File.ReadAllBytes(Path.Combine(Root, @"technical\extracted\bar\us\fontimage\sys.rgb"));
        var spacing = File.ReadAllBytes(Path.Combine(Root, @"technical\extracted\bar\us\fontinfo\sys.list"));
        var charCell = new Dictionary<char, int>();
        foreach (var line in File.ReadLines(Path.Combine(Root, @"font-rtl\arabic\codemap.tsv")).Skip(1))
        {
            var p = line.Split('\t');
            if (p.Length < 11 || p[10] != "GLYPH" || p[5].Length != 1) continue;
            int cell = int.Parse(p[1]);
            if (cell >= 0) charCell[p[5][0]] = cell;
        }

        Console.WriteLine("== original atlas reference boxes (baseline check) ==");
        foreach (var ch in "0ATg")
            if (charCell.TryGetValue(ch, out var cc))
            {
                var bb = CellBox(rgb, cc);
                Console.WriteLine($"  '{ch}' cell={cc} l={bb.l} r={bb.r} t={bb.t} b={bb.b} sp={spacing[cc]} sp/2={spacing[cc] / 2f:F1}");
            }

        const string Phrase = "السلام عليكم 123";
        const string Alpha = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي";
        var cands = new (string f, int s)[]
        {
            ("Tahoma", 14), ("Segoe UI", 13), ("Courier New", 14), ("Courier New", 16),
            ("MV Boli", 14),
            ("Traditional Arabic", 14), ("Traditional Arabic", 13), ("Sakkal Majalla", 14),
            ("Andalus", 17),
        };

        var rows = new List<(string label, Bitmap strip)>();

        // reference row: original cells only
        {
            var vis = Shape("THE QUICK 123");
            var strip = new Bitmap(700, CH, PixelFormat.Format32bppArgb);
            float end = ComposeVisual(vis, strip, rgb, spacing, charCell, null, 0, 0, 4);
            rows.Add(("ORIGINAL atlas  THE QUICK 123", Crop(strip, (int)end + 4)));
        }

        foreach (var (fn, sz) in cands)
        {
            using var f = new Font(fn, sz, FontStyle.Regular, GraphicsUnit.Pixel);
            var alef = RenderGlyph(Ar.Pf['ا'][0], f, 1f);
            if (alef.bmp == null) { Console.WriteLine($"!! no alef ink @ {fn} {sz}"); continue; }
            int bl = alef.b;
            alef.bmp.Dispose();

            var glyphs = new Dictionary<(char, int), (Bitmap bmp, int t, int w)>();
            int maxAsc = 0, maxDesc = 0, nSq = 0, missing = 0;
            double kxSum = 0; int kxN = 0; float minKx = 1;
            foreach (var (letter, form) in Ar.Needed())
            {
                int cp = Ar.Pf[letter][form];
                var g1 = RenderGlyph(cp, f, 1f);
                if (g1.bmp == null) { missing++; Console.WriteLine($"  !! no ink U+{cp:X4} {letter} form{form} @ {fn} {sz}"); continue; }
                maxAsc = Math.Max(maxAsc, bl - g1.t);
                maxDesc = Math.Max(maxDesc, g1.b - bl);
                int natW = g1.r - g1.l + 1;
                float kx = natW > CW ? (float)CW / natW : 1f;
                if (kx == 1f) glyphs[(letter, form)] = (g1.bmp, g1.t, natW);
                else
                {
                    g1.bmp.Dispose();
                    var g2 = RenderGlyph(cp, f, kx);
                    if (g2.bmp == null) { missing++; continue; }
                    glyphs[(letter, form)] = (g2.bmp, g2.t, g2.r - g2.l + 1);
                }
                kxSum += kx; kxN++;
                if (kx < 1f) { nSq++; minKx = Math.Min(minKx, kx); }
            }

            int baseY = Math.Min(20, CH - 1 - maxDesc);
            int keepShift = 20 - baseY;
            double kxAvg = kxN > 0 ? kxSum / kxN : 1;
            string label = $"{fn} {sz}px   base={baseY} keepShift={keepShift} asc={maxAsc} desc={maxDesc} kX avg={kxAvg:F2} min={minKx:F2} squeezed={nSq} missing={missing}";
            Console.WriteLine(label);

            var strip = new Bitmap(700, CH, PixelFormat.Format32bppArgb);
            using (var gr = Graphics.FromImage(strip))
            {
                gr.Clear(Color.Transparent);
                // guides: kept-cap-top (baseline-13 after shift), baseline, cell bottom 23
                gr.FillRectangle(new SolidBrush(Color.FromArgb(70, 255, 255, 255)), 0, baseY - 13, 700, 1);
                gr.FillRectangle(new SolidBrush(Color.FromArgb(150, 255, 60, 60)), 0, baseY, 700, 1);
                gr.FillRectangle(new SolidBrush(Color.FromArgb(70, 255, 255, 255)), 0, 23, 700, 1);
            }
            float end1 = ComposeVisual(ToVisual(Shape(Phrase)), strip, rgb, spacing, charCell, glyphs, baseY, bl, 6, keepShift);
            // isolated-forms row: force form=iso, jp=false
            var iso = Alpha.Select(ch => (ch, 0, false)).ToList();
            float end2 = ComposeVisual(iso, strip, rgb, spacing, charCell, glyphs, baseY, bl, end1 + 10, keepShift);
            int usedW = (int)Math.Max(end1, end2) + 4;
            rows.Add((label, Crop(strip, usedW)));
        }

        // assemble vertically, upscale x4 nearest
        const int scale = 4, labelH = 17, rowGap = 7, marginX = 12;
        int maxStripW = rows.Max(r => r.strip.Width);
        int totalW = marginX * 2 + maxStripW * scale;
        int totalH = marginX + rows.Count() * (labelH + CH * scale + rowGap);
        using var outBmp = new Bitmap(totalW, totalH, PixelFormat.Format32bppArgb);
        using (var g = Graphics.FromImage(outBmp))
        {
            g.Clear(Color.FromArgb(25, 25, 30));
            using var lblFont = new Font("Segoe UI", 11, FontStyle.Bold);
            using var brush = new SolidBrush(Color.Gainsboro);
            int y = marginX;
            foreach (var (lbl, strip) in rows)
            {
                g.DrawString(lbl, lblFont, brush, marginX, y);
                y += labelH;
                using var up = Upscale(strip, scale);
                g.DrawImage(up, marginX, y);
                y += CH * scale + rowGap;
            }
        }
        var outPath = Path.Combine(Root, @"font-rtl\arabic\preview.png");
        outBmp.Save(outPath, ImageFormat.Png);
        Console.WriteLine($"wrote {outPath}  {totalW}x{totalH}");
        return 0;
    }

    static Bitmap Crop(Bitmap src, int w)
    {
        w = Math.Min(w, src.Width);
        return src.Clone(new Rectangle(0, 0, w, src.Height), PixelFormat.Format32bppArgb);
    }

    static Bitmap Upscale(Bitmap src, int k)
    {
        var dst = new Bitmap(src.Width * k, src.Height * k, PixelFormat.Format32bppArgb);
        using var g = Graphics.FromImage(dst);
        g.InterpolationMode = InterpolationMode.NearestNeighbor;
        g.PixelOffsetMode = PixelOffsetMode.Half;
        g.DrawImage(src, 0, 0, dst.Width, dst.Height);
        return dst;
    }

    static int Map()
    {
        var usDir = Path.Combine(Root, @"technical\extracted\game-data\original\msg\us");

        var kind = new string[256];
        var chOf = new string[256];
        for (int b = 0; b < 256; b++)
        {
            var buf = new byte[8]; buf[0] = (byte)b;
            try
            {
                var first = P.Decode(buf).FirstOrDefault();
                if (first == null) { kind[b] = "none"; continue; }
                kind[b] = P.Cmd(first) ?? "?";
                chOf[b] = P.Text(first);
            }
            catch (Exception e) { kind[b] = "THROW:" + (e.InnerException?.Message ?? e.Message); }
        }

        var charToCode = new Dictionary<char, int>();
        for (int b = 0x20; b <= 0xFF; b++)
            if (kind[b] is "PrintText" && chOf[b] is { Length: 1 })
                charToCode[chOf[b][0]] = b;
        var complexLabelToCode = new Dictionary<string, int>();
        for (int b = 0x20; b <= 0xFF; b++)
            if (kind[b] is "PrintComplex" && !string.IsNullOrEmpty(chOf[b]))
                complexLabelToCode[chOf[b]] = b;

        var textCount = new long[256];
        var rawCount = new long[256];
        long nMsg = 0, nFail = 0, nText = 0, nComplex = 0, nUnmapped = 0;
        foreach (var f in Directory.GetFiles(usDir, "*.bar"))
        {
            var bn = Path.GetFileName(f);
            if (bn is "fontimage.bar" or "fontinfo.bar") continue;
            foreach (var be in (System.Collections.IEnumerable)P.BarRead(f))
            {
                var st = be.GetType().GetProperty("Stream")?.GetValue(be) as Stream;
                if (st == null) continue;
                st.Position = 0;
                List<object> entries;
                try { entries = P.MsgRead(st); } catch { continue; }
                foreach (var e in entries)
                {
                    var data = (byte[])e.GetType().GetProperty("Data").GetValue(e);
                    nMsg++;
                    foreach (var x in data) rawCount[x]++;
                    try
                    {
                        foreach (var m in P.Decode(data))
                        {
                            var c = P.Cmd(m);
                            if (c != "PrintText" && c != "PrintComplex") continue;
                            if (c == "PrintText") nText++; else nComplex++;
                            var s = P.Text(m);
                            if (string.IsNullOrEmpty(s)) continue;
                            if (c == "PrintComplex")
                            {
                                if (complexLabelToCode.TryGetValue(s, out var cc)) textCount[cc]++;
                                else nUnmapped++;
                                continue;
                            }
                            foreach (var ch in s)
                                if (charToCode.TryGetValue(ch, out var code)) textCount[code]++;
                                else nUnmapped++;
                        }
                    }
                    catch { nFail++; }
                }
            }
        }
        Console.WriteLine($"messages={nMsg} decodeFail={nFail} textModels={nText} complexModels={nComplex} unmappedChars={nUnmapped}");

        var rgb = File.ReadAllBytes(Path.Combine(Root, @"technical\extracted\bar\us\fontimage\sys.rgb"));
        Console.WriteLine($"sys.rgb = {rgb.Length} bytes (expect 65536)");
        var ink = new int[280];
        for (int cell = 0; cell < 280; cell++)
        {
            int x0 = (cell % COLS) * CW, y0 = (cell / COLS) * CH;
            int n = 0;
            for (int y = y0; y < y0 + CH; y++)
                for (int x = x0; x < x0 + CW; x++)
                    if (rgb[y * 256 + x] != 0) n++;
            ink[cell] = n;
        }

        var sb = new StringBuilder();
        sb.AppendLine("code\tcell\tcol\trow\tkind\tchar\tcharCode\ttextCount\trawCount\tinkPx\tverdict");
        for (int b = 0; b < 256; b++)
        {
            if (b < 0x20 && kind[b] == "none") continue;
            var cell = b - 0x20;
            var inGrid = cell >= 0 && cell < COLS * ROWS;
            var ch = chOf[b] ?? "";
            var verdict =
                b < 0x20 ? "COMMAND" :
                !inGrid ? "OUT-OF-GRID" :
                kind[b] is "Unsupported" or "Tabulation" ? "FORBIDDEN" :
                kind[b] is "PrintText" or "PrintComplex" ? (ink[cell] > 0 ? "GLYPH" : "GLYPH-EMPTY") :
                "OTHER";
            sb.AppendLine(string.Join("\t",
                $"{b:X2}", cell,
                inGrid ? (cell % COLS).ToString() : "-",
                inGrid ? (cell / COLS).ToString() : "-",
                kind[b], ch,
                ch.Length == 1 ? ((int)ch[0]).ToString("X4") : "",
                textCount[b], rawCount[b],
                inGrid ? ink[cell].ToString() : "-", verdict));
        }
        var outTsv = Path.Combine(Root, @"font-rtl\arabic\codemap.tsv");
        File.WriteAllText(outTsv, sb.ToString(), new UTF8Encoding(false));
        Console.WriteLine($"wrote {outTsv}");

        var glyphs = Enumerable.Range(0x20, 224)
            .Where(b => kind[b] is "PrintText" or "PrintComplex" && ink[b - 0x20] > 0).ToList();
        var forbidden = Enumerable.Range(0x20, 224).Where(b => kind[b] is "Unsupported" or "Tabulation").ToList();
        var emptyGlyph = Enumerable.Range(0x20, 224).Where(b => kind[b] is "PrintText" or "PrintComplex" && ink[b - 0x20] == 0).ToList();

        Console.WriteLine($"\naddressable cells (0x20..0xFF) = 224");
        Console.WriteLine($"GLYPH cells with ink           = {glyphs.Count}");
        Console.WriteLine($"FORBIDDEN (Unsupported/Tab)    = {forbidden.Count}: {string.Join(" ", forbidden.Select(b => $"{b:X2}"))}");
        Console.WriteLine($"empty glyph cells              = {emptyGlyph.Count}: {string.Join(" ", emptyGlyph.Select(b => $"{b:X2}"))}");

        Console.WriteLine("\n== glyph cells sorted by decoded text usage (ascending) ==");
        foreach (var b in glyphs.OrderBy(b => textCount[b]).ThenBy(b => b))
            Console.WriteLine($"  {b:X2} cell={(b - 0x20),3} col={(b - 0x20) % COLS,2} row={(b - 0x20) / COLS,-2} '{chOf[b]}' text={textCount[b],6} ink={ink[b - 0x20],3}");
        return 0;
    }
}
