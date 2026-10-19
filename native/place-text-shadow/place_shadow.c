/* Panacea test plugin: select the game's single drop shadow for place labels.
   Only two verified font-mode immediate bytes change in loaded memory.
   Original executable, fonts, messages, sizing and positioning are untouched. */
#include <windows.h>
#include <stdint.h>
#include <stddef.h>
#ifdef PLACE_TEST
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#endif

#define IMAGE_SIZE 0x2c2b000u
#define GUIDE 0x168350u
#define PLACE 0x1683d0u
#define GUIDE_MODE (GUIDE + 23u)
#define PLACE_MODE (PLACE + 37u)

static const unsigned char guide_bytes[] = {
 0x48,0x83,0xec,0x48,0x48,0x8b,0x51,0x20,0x41,0xb9,0x80,0x01,0x00,0x00,
 0xc7,0x44,0x24,0x30,0x04,0x00,0x00,0x00,0xb9,0x02,0x00,0x00,0x00,
 0xc7,0x44,0x24,0x28,0x00,0x00,0x00,0x00,0xc7,0x44,0x24,0x20,0xff,0xff,
 0xff,0x80,0x45,0x8d,0x41,0x80,0xe8,0x4c,0x6b,0x24,0x00,0x48,0x83,0xc4,0x48,0xc3
};
static const unsigned char place_bytes[] = {
 0x40,0x53,0x48,0x83,0xec,0x40,0x48,0x8b,0xd9,0xe8,0xb2,0xea,0xff,0xff,
 0x84,0xc0,0x75,0x30,0x48,0x8b,0x53,0x20,0x41,0xb9,0xc0,0x00,0x00,0x00,
 0xc7,0x44,0x24,0x30,0x04,0x00,0x00,0x00,0xb9,0x02,0x00,0x00,0x00,
 0xc7,0x44,0x24,0x28,0x00,0x00,0x00,0x00,0xc7,0x44,0x24,0x20,0xff,0xff,
 0xff,0x80,0x45,0x8d,0x41,0x40,0xe8,0xbe,0x6a,0x24,0x00,0x48,0x83,0xc4,0x40,0x5b,0xc3
};

static int equal_bytes(const unsigned char *a, const unsigned char *b, size_t n) {
 for (size_t i=0; i<n; ++i) if (a[i]!=b[i]) return 0;
 return 1;
}

/* Refuse any other game build, another mod's code edits, or partial matches. */
static int compatible(const unsigned char *base, size_t size) {
 if (size!=IMAGE_SIZE || base[0]!='M' || base[1]!='Z') return 0;
 uint32_t pe_offset=*(const uint32_t *)(base+0x3c);
 if (pe_offset>4096 || pe_offset+sizeof(IMAGE_NT_HEADERS64)>size) return 0;
 const IMAGE_NT_HEADERS64 *nt=(const IMAGE_NT_HEADERS64 *)(base+pe_offset);
 if (nt->Signature!=IMAGE_NT_SIGNATURE || nt->FileHeader.Machine!=IMAGE_FILE_MACHINE_AMD64 ||
     nt->FileHeader.TimeDateStamp!=0x669e384a || nt->OptionalHeader.Magic!=IMAGE_NT_OPTIONAL_HDR64_MAGIC ||
     nt->OptionalHeader.SizeOfImage!=IMAGE_SIZE) return 0;
 return equal_bytes(base+GUIDE,guide_bytes,sizeof(guide_bytes)) &&
        equal_bytes(base+PLACE,place_bytes,sizeof(place_bytes));
}

typedef int (*Commit)(unsigned char *);
static int apply(unsigned char *base, size_t size, Commit commit) {
 if (!compatible(base,size)) return -2;
 return commit(base) ? 1 : -3;
}

static int commit_memory(unsigned char *base) {
 DWORD old_protection, ignored;
 SIZE_T length=PLACE+sizeof(place_bytes)-GUIDE;
 if (!VirtualProtect(base+GUIDE,length,PAGE_EXECUTE_READWRITE,&old_protection)) return 0;
 /* Mode 1 uses the same sys atlas and metrics, with one native shadow copy.
    Mode 2 emits eight outline copies before each connected Arabic character. */
 base[GUIDE_MODE]=1;
 base[PLACE_MODE]=1;
 if (!FlushInstructionCache(GetCurrentProcess(),base+GUIDE,length) ||
     !VirtualProtect(base+GUIDE,length,old_protection,&ignored)) {
  base[GUIDE_MODE]=2; base[PLACE_MODE]=2;
  FlushInstructionCache(GetCurrentProcess(),base+GUIDE,length);
  VirtualProtect(base+GUIDE,length,old_protection,&ignored);
  return 0;
 }
 return 1;
}

static volatile LONG status;
__declspec(dllexport) LONG GetStatus(void) { return status; }

__declspec(dllexport) void OnInit(const wchar_t *mod_folder) {
 (void)mod_folder;
 if (status) return;
 wchar_t name[MAX_PATH];
 DWORD count=GetModuleFileNameW(NULL,name,MAX_PATH);
 if (!count || count>=MAX_PATH) { status=-1; return; }
 const wchar_t *leaf=name;
 for (DWORD i=0; i<count; ++i) if (name[i]=='\\' || name[i]=='/') leaf=name+i+1;
 const wchar_t expected[]=L"kingdom hearts ii final mix.exe";
 size_t i=0;
 for (;expected[i] && leaf[i];++i) {
  wchar_t c=leaf[i]; if (c>='A' && c<='Z') c+=32;
  if(c!=expected[i]) { status=-1; return; }
 }
 if(expected[i] || leaf[i]) { status=-1; return; }
 unsigned char *base=(unsigned char *)GetModuleHandleW(NULL);
 status=apply(base,IMAGE_SIZE,commit_memory);
}

BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved) {
 (void)instance; (void)reason; (void)reserved;
 return TRUE;
}

#ifdef PLACE_TEST
static int writes;
static int test_commit(unsigned char *base) {
 ++writes; base[GUIDE_MODE]=1; base[PLACE_MODE]=1; return 1;
}
static int deny_commit(unsigned char *base) { (void)base; return 0; }
#define CHECK(x) do { if(!(x)) { printf("FAIL line %d\n",__LINE__); return 1; } } while(0)
static void seed(unsigned char *base) {
 memset(base,0,IMAGE_SIZE); base[0]='M';base[1]='Z';
 *(uint32_t *)(base+0x3c)=0x80;
 IMAGE_NT_HEADERS64 *nt=(IMAGE_NT_HEADERS64 *)(base+0x80);
 nt->Signature=IMAGE_NT_SIGNATURE;nt->FileHeader.Machine=IMAGE_FILE_MACHINE_AMD64;
 nt->FileHeader.TimeDateStamp=0x669e384a;nt->OptionalHeader.Magic=IMAGE_NT_OPTIONAL_HDR64_MAGIC;
 nt->OptionalHeader.SizeOfImage=IMAGE_SIZE;
 memcpy(base+GUIDE,guide_bytes,sizeof(guide_bytes));memcpy(base+PLACE,place_bytes,sizeof(place_bytes));
}
int main(void) {
 unsigned char *base=malloc(IMAGE_SIZE),*before=malloc(IMAGE_SIZE);
 CHECK(base && before);
 seed(base);memcpy(before,base,IMAGE_SIZE);
 CHECK(apply(base,IMAGE_SIZE,test_commit)==1 && writes==1);
 size_t differences=0;
 for(size_t i=0;i<IMAGE_SIZE;++i) if(base[i]!=before[i]) {
  CHECK((i==GUIDE_MODE || i==PLACE_MODE) && base[i]==1 && before[i]==2);++differences;
 }
 CHECK(differences==2);
 CHECK(apply(base,IMAGE_SIZE,test_commit)==-2 && writes==1);
 seed(base);base[GUIDE]^=1;CHECK(apply(base,IMAGE_SIZE,test_commit)==-2 && writes==1);
 seed(base);base[PLACE+60]^=1;CHECK(apply(base,IMAGE_SIZE,test_commit)==-2 && writes==1);
 seed(base);base[0]=0;CHECK(apply(base,IMAGE_SIZE,test_commit)==-2 && writes==1);
 seed(base);*(uint32_t *)(base+0x3c)=0xffffffff;CHECK(apply(base,IMAGE_SIZE,test_commit)==-2 && writes==1);
 seed(base);((IMAGE_NT_HEADERS64 *)(base+0x80))->FileHeader.TimeDateStamp++;
 CHECK(apply(base,IMAGE_SIZE,test_commit)==-2 && writes==1);
 seed(base);CHECK(apply(base,IMAGE_SIZE-1,test_commit)==-2 && writes==1);
 CHECK(apply(base,IMAGE_SIZE,deny_commit)==-3 && base[GUIDE_MODE]==2 && base[PLACE_MODE]==2);
 /* Real protection/cache operations exercised on a private synthetic image. */
 CHECK(apply(base,IMAGE_SIZE,commit_memory)==1 && base[GUIDE_MODE]==1 && base[PLACE_MODE]==1);
 OnInit(NULL);CHECK(GetStatus()==-1);
 free(before);free(base);puts("PASS: two-byte scope, guards, repeat refusal, denied write, private-memory protection, non-game host refusal");
 return 0;
}
#endif
