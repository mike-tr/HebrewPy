#include <algorithm>
#include <fcntl.h> // for _setmode
#include <io.h>
#include <iostream>
#include <windows.h>
using namespace std;

std::wstring operator+(const int b, const std::wstring &a) {
    return std::to_wstring(b) + a;
}

std::wstring operator+(const double b, const std::wstring &a) {
    return std::to_wstring(b) + a;
}

std::wstring operator+(const std::wstring &a, const int b) {
    return a + std::to_wstring(b);
}

std::wstring operator+(const std::wstring &a, const double b) {
    return a + std::to_wstring(b);
}

std::wstring reverse(const std::wstring &str) {
    std::wstring ret;
    for (auto it = str.end() - 1; it != str.begin() - 1; --it)
        ret += *it;
    return ret;
}

void main_hebrew();

int main() {
    _setmode(_fileno(stdout), _O_U16TEXT);
    main_hebrew();
    return 0;
}

void main_hebrew() {
	auto א = 30;
	auto אנוכי = std::wstring(L"מיכאל");
	auto ב = 8.3;
	auto ג = std::wstring(L"שלום עולם");
	auto משפט = std::wstring(L"היה לי משעמם");
	std::wcout << reverse(ג) << std::endl;
	auto ד = אנוכי + std::wstring(L" : ") + משפט;
	std::wcout << reverse(ד) << std::endl;
	std::wcout << reverse(אנוכי + std::wstring(L" : ") + משפט) << std::endl;
	std::wcout << reverse(std::wstring(L" זה לקח ") + ב + std::wstring(L" שעות שזה : ") +  ( ב * 60 / 60 * 60 *  ( 12 / 2 * 10 )  )  + std::wstring(L" שניות.")) << std::endl;
	auto ה = 50 * 10 /  ( 50 * 10 ) ;
	std::wcout << ה << std::endl;
	if (א < ב) {
		std::wcout << reverse(std::wstring(L"א גדול מ ב")) << std::endl;
		std::wcout << א << std::endl;
		if (א + ב > א) {
			std::wcout << reverse(std::wstring(L"ברור")) << std::endl;
			auto א = 33;
			std::wcout << reverse(std::wstring(L"א חדש = ") + א) << std::endl;
		} else {
			std::wcout << reverse(std::wstring(L"???")) << std::endl;
			std::wcout << reverse(std::wstring(L"סוף א > ב")) << std::endl;
		}
	} else {
		std::wcout << reverse(std::wstring(L"ב גדול מ א")) << std::endl;
		std::wcout << ב << std::endl;
	}
	std::wcout << א + ב << std::endl;
	std::wcout << reverse(ג) << std::endl;
	while (א > 0) {
		std::wcout << reverse(std::wstring(L"א = ") + א) << std::endl;
		if (א > 10) {
			std::wcout << reverse(std::wstring(L"א>10")) << std::endl;
			if (א > 20) {
				std::wcout << reverse(std::wstring(L"וגם א>20 : ") + א) << std::endl;
				א = א - 2;
			} else {
				std::wcout << reverse(std::wstring(L"וגם א<20 : ") + א) << std::endl;
				א = א - 1;
			}
			א = א - 1;
			std::wcout << reverse(std::wstring(L"סוף א>10 : ") + א) << std::endl;
		} else if (א > 5) {
			א = א - 1;
			std::wcout << reverse(std::wstring(L"א>5")) << std::endl;
		} else {
			std::wcout << reverse(std::wstring(L"א<5")) << std::endl;
		}
		א = א - 1;
	}
	if (א > ב) {
		std::wcout << reverse(std::wstring(L"איך?")) << std::endl;
	} else {
		std::wcout << reverse(std::wstring(L"הגיוני")) << std::endl;
	}
	if (א == 0) {
		std::wcout << reverse(std::wstring(L"סוף")) << std::endl;
	}
}