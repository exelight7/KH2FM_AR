#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <sddl.h>
#include <objbase.h>
#include <string>
#include <vector>

static void Error(const wchar_t* message) {
    MessageBoxW(nullptr, message, L"أداة إزالة تعريب KH2FM", MB_OK | MB_ICONERROR | MB_RTLREADING | MB_RIGHT);
}

static bool Extract(HINSTANCE instance, int id, const std::wstring& file) {
    HRSRC resource = FindResourceW(instance, MAKEINTRESOURCEW(id), RT_RCDATA);
    if (!resource) return false;
    DWORD size = SizeofResource(instance, resource);
    const void* data = LockResource(LoadResource(instance, resource));
    if (!size || !data) return false;
    HANDLE handle = CreateFileW(file.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (handle == INVALID_HANDLE_VALUE) return false;
    DWORD written = 0;
    bool ok = WriteFile(handle, data, size, &written, nullptr) && written == size;
    if (ok) ok = FlushFileBuffers(handle) != FALSE;
    CloseHandle(handle);
    return ok;
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int) {
    wchar_t windowsDir[MAX_PATH], systemDir[MAX_PATH], guidText[40];
    if (!GetWindowsDirectoryW(windowsDir, MAX_PATH) || !GetSystemDirectoryW(systemDir, MAX_PATH)) {
        Error(L"تعذر تحديد مجلد Windows."); return 1;
    }
    std::wstring powershell = std::wstring(systemDir) + L"\\WindowsPowerShell\\v1.0\\powershell.exe";
    if (GetFileAttributesW(powershell.c_str()) == INVALID_FILE_ATTRIBUTES) {
        Error(L"لم أجد Windows PowerShell المطلوب لتشغيل الأداة."); return 1;
    }
    GUID guid;
    if (FAILED(CoCreateGuid(&guid)) || !StringFromGUID2(guid, guidText, 40)) return 1;
    std::wstring directory = std::wstring(windowsDir) + L"\\Temp\\KH2AR-Remover-" + guidText;
    PSECURITY_DESCRIPTOR descriptor = nullptr;
    if (!ConvertStringSecurityDescriptorToSecurityDescriptorW(L"D:P(A;;FA;;;SY)(A;;FA;;;BA)", SDDL_REVISION_1, &descriptor, nullptr)) return 1;
    SECURITY_ATTRIBUTES security{sizeof(SECURITY_ATTRIBUTES), descriptor, FALSE};
    bool created = CreateDirectoryW(directory.c_str(), &security) != FALSE;
    LocalFree(descriptor);
    if (!created) { Error(L"تعذر تجهيز الأداة. شغل الملف بصلاحيات المسؤول."); return 1; }
    const std::vector<std::wstring> names{L"Remover.ps1", L"Remover.Core.ps1", L"manifest_1.0.1.csv", L"manifest_panacea.csv", L"manifest_1.0.2.csv"};
    bool complete = true;
    for (size_t i = 0; i < names.size(); ++i) {
        if (!Extract(instance, 101 + static_cast<int>(i), directory + L"\\" + names[i])) { complete = false; break; }
    }
    DWORD exitCode = 1;
    if (complete) {
        std::wstring command = L"\"" + powershell + L"\" -NoLogo -NoProfile -STA -ExecutionPolicy Bypass -File \"" + directory + L"\\Remover.ps1\"";
        std::vector<wchar_t> buffer(command.begin(), command.end()); buffer.push_back(0);
        STARTUPINFOW startup{}; startup.cb = sizeof(startup);
        PROCESS_INFORMATION process{};
        if (CreateProcessW(powershell.c_str(), buffer.data(), nullptr, nullptr, FALSE, CREATE_NO_WINDOW, nullptr, directory.c_str(), &startup, &process)) {
            WaitForSingleObject(process.hProcess, INFINITE);
            GetExitCodeProcess(process.hProcess, &exitCode);
            CloseHandle(process.hThread); CloseHandle(process.hProcess);
        } else { Error(L"تعذر تشغيل واجهة الأداة. لم يتغير التعريب."); }
    } else { Error(L"تعذر تجهيز ملفات الأداة. لم يتغير التعريب."); }
    for (const auto& name : names) DeleteFileW((directory + L"\\" + name).c_str());
    RemoveDirectoryW(directory.c_str());
    return static_cast<int>(exitCode);
}
