/* Normalize the default label height in active green command rows only.
   Preserve the native key icon, explicit message sizes and all other UI. */
#include <windows.h>
#include <stdint.h>
#include <stddef.h>
#include "guard_pattern.h"
#ifdef GREEN_TEST
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#endif

#define IMAGE_SIZE 0x2c2b000u
#define DRAW_RVA 0x15b4a0u
#define SLOT_RVA 0x5b1c08u
#define ROOT_RVA 0xabc508u
#define LIMIT 1024u
typedef uintptr_t (*Draw)(void *);
static unsigned char *image;
static Draw original_draw;
static volatile LONG status, normalized_count;

static size_t token_size(unsigned char c) {
 if(c>=0x20 || c==1 || c==2 || c==3 || c==0x0c || c==0x0d || c==0x10) return 1;
 switch(c) {
  case 4:case 6:case 9:case 10:case 11:case 14:case 22:case 26:case 27:case 28:return 2;
  case 18:case 20:case 21:case 23:case 24:return 3;
  case 8:return 4;
  case 7:case 17:case 19:return 5;
  case 15:return 6;
  default:return 0;
 }
}

/* Zero bytes inside positioning/color arguments are not message terminators. */
static size_t normalize(const unsigned char *src,size_t bound,unsigned char *out,size_t capacity) {
 size_t n=0;
 while(n<bound && src[n]) {
  size_t step=token_size(src[n]);
  if(!step || step>bound-n) return 0;
  n+=step;
 }
 if(n==bound || !n || n+3>capacity) return 0;
 ++n;
 size_t label=(n>12 && src[0]==0x11 && src[5]==9 && src[7]==0x11) ? 12 : 0;
 if(!src[label] || src[label]==0x0a) return 0;
 for(size_t i=0;i<label;++i) out[i]=src[i];
 out[label]=0x0a;out[label+1]=20;
 for(size_t i=label;i<n;++i) out[i+2]=src[i];
 return n+2;
}
#ifdef GREEN_TEST_API
__declspec(dllexport) size_t TestNormalize(const unsigned char *src,size_t bound,unsigned char *out,size_t capacity) {
 return normalize(src,bound,out,capacity);
}
#endif

static int green_row(const unsigned char *object) {
 int group=*(const int *)(object+0x178);
 if(group!=0 && group!=1 && group!=2 && group!=3 && group!=5) return 0;
 uintptr_t root=*(const uintptr_t *)(image+ROOT_RVA),base=(uintptr_t)image;
 if(root<base || root>base+IMAGE_SIZE-0x140) return 0;
 /* Native COMMAND_MAIN owns four sets of nine active reaction-row slots. */
 for(size_t i=0;i<36;++i)
  if(*(const uintptr_t *)(root+0x20+i*8)==(uintptr_t)object) return 1;
 return 0;
}

static uintptr_t draw_green(void *value) {
 unsigned char *object=value;
 const unsigned char *message=*(const unsigned char **)(object+0x1f8);
 if(!message || !green_row(object)) return original_draw(value);
 MEMORY_BASIC_INFORMATION info;
 if(!VirtualQuery(message,&info,sizeof(info)) || info.State!=MEM_COMMIT ||
    (info.Protect&(PAGE_NOACCESS|PAGE_GUARD))) return original_draw(value);
 uintptr_t end=(uintptr_t)info.BaseAddress+info.RegionSize,start=(uintptr_t)message;
 if(end<=start) return original_draw(value);
 size_t available=end-start;if(available>LIMIT) available=LIMIT;
 unsigned char buffer[LIMIT+2];
 if(!normalize(message,available,buffer,sizeof(buffer))) return original_draw(value);
 *(const unsigned char **)(object+0x1f8)=buffer;
 InterlockedIncrement(&normalized_count);
 uintptr_t result=original_draw(value);
 *(const unsigned char **)(object+0x1f8)=message;
 return result;
}

static int equal_bytes(const unsigned char *a,const unsigned char *b,size_t size) {
 for(size_t i=0;i<size;++i) if(a[i]!=b[i]) return 0;
 return 1;
}
static int compatible(const unsigned char *base,size_t size) {
 if(size!=IMAGE_SIZE || base[0]!='M' || base[1]!='Z') return 0;
 uint32_t offset=*(const uint32_t *)(base+0x3c);
 if(offset>4096 || offset+sizeof(IMAGE_NT_HEADERS64)>size) return 0;
 const IMAGE_NT_HEADERS64 *nt=(const IMAGE_NT_HEADERS64 *)(base+offset);
 if(nt->Signature!=IMAGE_NT_SIGNATURE || nt->FileHeader.Machine!=IMAGE_FILE_MACHINE_AMD64 ||
    nt->FileHeader.TimeDateStamp!=0x669e384a || nt->OptionalHeader.Magic!=IMAGE_NT_OPTIONAL_HDR64_MAGIC ||
    nt->OptionalHeader.SizeOfImage!=IMAGE_SIZE) return 0;
 return *(const uintptr_t *)(base+SLOT_RVA)==(uintptr_t)(base+DRAW_RVA) &&
        equal_bytes(base+DRAW_RVA,draw_pattern,sizeof(draw_pattern));
}
static int install(unsigned char *base,size_t size) {
 if(!compatible(base,size)) return -2;
 DWORD old,ignored;void **slot=(void **)(base+SLOT_RVA);
 if(!VirtualProtect(slot,sizeof(*slot),PAGE_READWRITE,&old)) return -3;
 image=base;original_draw=(Draw)(base+DRAW_RVA);
 InterlockedExchangePointer(slot,(void *)draw_green);
 if(!VirtualProtect(slot,sizeof(*slot),old,&ignored)) {
  InterlockedExchangePointer(slot,(void *)original_draw);
  VirtualProtect(slot,sizeof(*slot),old,&ignored);return -3;
 }
 return 1;
}
__declspec(dllexport) LONG GetStatus(void) { return status; }
__declspec(dllexport) LONG GetNormalizedCount(void) { return normalized_count; }
__declspec(dllexport) void OnInit(const wchar_t *folder) {
 (void)folder;if(status) return;
 wchar_t path[MAX_PATH];DWORD length=GetModuleFileNameW(NULL,path,MAX_PATH);
 if(!length || length>=MAX_PATH){status=-1;return;}
 const wchar_t *leaf=path;
 for(DWORD i=0;i<length;++i)if(path[i]=='/' || path[i]=='\\')leaf=path+i+1;
 const wchar_t expected[]=L"kingdom hearts ii final mix.exe";size_t i=0;
 for(;expected[i] && leaf[i];++i){wchar_t c=leaf[i];if(c>='A' && c<='Z')c+=32;if(c!=expected[i]){status=-1;return;}}
 if(expected[i] || leaf[i]){status=-1;return;}
 status=install((unsigned char *)GetModuleHandleW(NULL),IMAGE_SIZE);
}
BOOL WINAPI DllMain(HINSTANCE instance,DWORD reason,LPVOID reserved) {
 (void)instance;(void)reason;(void)reserved;return TRUE;
}

#ifdef GREEN_TEST
#define CHECK(x) do{if(!(x)){printf("FAIL line %d\n",__LINE__);return 1;}}while(0)
static const unsigned char pickup[]={0x11,0xeb,0xff,0x1c,0,9,0xdf,0x11,2,0,0x1c,0,0x38,0x86,0x9d,0xca,0x9a,0xbe,0};
static const unsigned char *during_message;
static size_t during_length;
static int calls,good;
static uintptr_t fake_draw(void *object) {
 ++calls;const unsigned char *p=*(const unsigned char **)((unsigned char *)object+0x1f8);
 good=equal_bytes(p,during_message,during_length);
 return 0x12345678u;
}
static void seed(unsigned char *base) {
 memset(base,0,IMAGE_SIZE);base[0]='M';base[1]='Z';*(uint32_t *)(base+0x3c)=0x80;
 IMAGE_NT_HEADERS64 *nt=(IMAGE_NT_HEADERS64 *)(base+0x80);
 nt->Signature=IMAGE_NT_SIGNATURE;nt->FileHeader.Machine=IMAGE_FILE_MACHINE_AMD64;
 nt->FileHeader.TimeDateStamp=0x669e384a;nt->OptionalHeader.Magic=IMAGE_NT_OPTIONAL_HDR64_MAGIC;
 nt->OptionalHeader.SizeOfImage=IMAGE_SIZE;
 memcpy(base+DRAW_RVA,draw_pattern,sizeof(draw_pattern));
 *(uintptr_t *)(base+SLOT_RVA)=(uintptr_t)(base+DRAW_RVA);
}
int main(void) {
 unsigned char out[LIMIT+2],again[LIMIT+2];size_t n=normalize(pickup,sizeof(pickup),out,sizeof(out));
 CHECK(n==sizeof(pickup)+2 && out[12]==0x0a && out[13]==20);
 CHECK(equal_bytes(out,pickup,12) && equal_bytes(out+14,pickup+12,sizeof(pickup)-12));
 CHECK(!normalize(out,n,again,sizeof(again)));
 unsigned char plain[]={0x38,0x86,0x9d,0};
 CHECK(normalize(plain,sizeof(plain),again,sizeof(again))==6 && again[0]==10 && again[1]==20);
 unsigned char custom[]={10,8,0x38,0};
 CHECK(!normalize(custom,sizeof(custom),again,sizeof(again)));
 unsigned char embedded[]={7,0,0,0,0,0x38,0};
 CHECK(normalize(embedded,sizeof(embedded),again,sizeof(again))==9);
 unsigned char unknown[]={5,0},unterminated[]={0x38,0x38},truncated[]={17,1,0};
 CHECK(!normalize(unknown,sizeof(unknown),again,sizeof(again)));
 CHECK(!normalize(unterminated,sizeof(unterminated),again,sizeof(again)));
 CHECK(!normalize(truncated,sizeof(truncated),again,sizeof(again)));
 CHECK(!normalize(plain,sizeof(plain),again,5));
 unsigned char *base=malloc(IMAGE_SIZE),*before=malloc(IMAGE_SIZE);CHECK(base && before);
 seed(base);memcpy(before,base,IMAGE_SIZE);
 CHECK(compatible(base,IMAGE_SIZE));CHECK(install(base,IMAGE_SIZE)==1);
 for(size_t i=0;i<IMAGE_SIZE;++i)if(base[i]!=before[i])CHECK(i>=SLOT_RVA && i<SLOT_RVA+8);
 CHECK(!compatible(base,IMAGE_SIZE));
 seed(base);base[DRAW_RVA]^=1;CHECK(install(base,IMAGE_SIZE)==-2);
 seed(base);((IMAGE_NT_HEADERS64 *)(base+0x80))->FileHeader.TimeDateStamp++;CHECK(!compatible(base,IMAGE_SIZE));
 seed(base);*(uint32_t *)(base+0x3c)=0xffffffff;CHECK(!compatible(base,IMAGE_SIZE));
 seed(base);CHECK(!compatible(base,IMAGE_SIZE-1));
 seed(base);image=base;original_draw=fake_draw;
 unsigned char object[0x220]={0},snapshot[0x220];
 *(uintptr_t *)(base+ROOT_RVA)=(uintptr_t)(base+0x2000);
 *(uintptr_t *)(base+0x2020)=(uintptr_t)object;
 *(int *)(object+0x178)=2;*(const unsigned char **)(object+0x1f8)=pickup;
 memcpy(snapshot,object,sizeof(object));during_message=out;during_length=n;
 CHECK(draw_green(object)==0x12345678u && calls==1 && good && normalized_count==1);
 CHECK(equal_bytes(snapshot,object,sizeof(object)));
 *(int *)(object+0x178)=7;during_message=pickup;during_length=sizeof(pickup);
 CHECK(draw_green(object)==0x12345678u && calls==2 && good && normalized_count==1);
 *(int *)(object+0x178)=2;*(uintptr_t *)(base+0x2020)=0;
 CHECK(draw_green(object)==0x12345678u && calls==3 && good && normalized_count==1);
 *(uintptr_t *)(base+0x2020)=(uintptr_t)object;*(const unsigned char **)(object+0x1f8)=out;
 during_message=out;during_length=n;
 CHECK(draw_green(object)==0x12345678u && calls==4 && good && normalized_count==1);
 OnInit(NULL);CHECK(GetStatus()==-1);
 free(before);free(base);
 puts("PASS: inline icon preserved, missing size normalized, explicit sizes retained, parser bounds, only active green rows, object restored, one vtable slot only, build guards, repeated install refusal");
 return 0;
}
#endif
