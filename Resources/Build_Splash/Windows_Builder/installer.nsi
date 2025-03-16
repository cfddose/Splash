;~ !include "MUI2.nsh"

;~ ; Define Installer Name and Output
;~ OutFile "SplashCaseCreatorSetup.exe"
;~ InstallDir "$PROGRAMFILES\SplashCaseCreator"
;~ RequestExecutionLevel admin

;~ ; Define branding and appearance
;~ !define MUI_ABORTWARNING
;~ !define MUI_ICON "../../Resources/Logos/simulitica_icon_logo.ico"
;~ !define MUI_UNICON "../../Resources/Logos/simulitica_icon_logo.ico"

;~ ; Define finish page text
;~ !define MUI_FINISHPAGE_TITLE "Installation Complete"
;~ !define MUI_FINISHPAGE_TEXT "SplashCaseCreator has been successfully installed. Click 'Finish' to start the application."
;~ !define MUI_FINISHPAGE_RUN "$INSTDIR\SplashCaseCreator.exe"
;~ !define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"

;~ ; Set installer pages
;~ !insertmacro MUI_PAGE_WELCOME
;~ !insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
;~ !insertmacro MUI_PAGE_DIRECTORY
;~ !insertmacro MUI_PAGE_INSTFILES
;~ !insertmacro MUI_PAGE_FINISH

;~ ; Set uninstaller pages
;~ !insertmacro MUI_UNPAGE_CONFIRM
;~ !insertmacro MUI_UNPAGE_INSTFILES

;~ ; Language settings
;~ !insertmacro MUI_LANGUAGE "English"

;~ ; Branding options
;~ Caption "SplashCaseCreator Installer"
;~ BrandingText "Powered by Simulitica Technologies"

;~ ; Install Section
;~ Section "Install"
    ;~ ; Set installation directory
    ;~ SetOutPath "$INSTDIR"

    ;~ ; Display progress
    ;~ DetailPrint "Preparing installation..."

    ;~ ; Copy all files from the build directory
    ;~ DetailPrint "Copying application files..."
    ;~ File /r "dist\SplashCaseCreator\*.*"

    ;~ ; Add README file
    ;~ DetailPrint "Copying README file..."
    ;~ File "README.txt"

    ;~ ; Add license file
    ;~ DetailPrint "Copying LICENSE file..."
    ;~ File "LICENSE.txt"

    ;~ ; Create desktop shortcut
    ;~ DetailPrint "Creating desktop shortcut..."
    ;~ CreateShortcut "$DESKTOP\SplashCaseCreator.lnk" "$INSTDIR\SplashCaseCreator.exe" \
        ;~ "" "$INSTDIR\SplashCaseCreator.exe" 0

    ;~ ; Create Start Menu folder
    ;~ DetailPrint "Creating Start Menu folder..."
    ;~ CreateDirectory "$SMPROGRAMS\SplashCaseCreator"

    ;~ ; Create Start Menu shortcuts
    ;~ DetailPrint "Creating Start Menu shortcuts..."
    ;~ CreateShortcut "$SMPROGRAMS\SplashCaseCreator\SplashCaseCreator.lnk" "$INSTDIR\SplashCaseCreator.exe" \
        ;~ "" "$INSTDIR\SplashCaseCreator.exe" 0
    ;~ CreateShortcut "$SMPROGRAMS\SplashCaseCreator\Uninstall.lnk" "$INSTDIR\Uninstall.exe" \
        ;~ "" "$INSTDIR\Uninstall.exe" 0
    ;~ CreateShortcut "$SMPROGRAMS\SplashCaseCreator\README.lnk" "$INSTDIR\README.txt" \
        ;~ "" "$INSTDIR\README.txt" 0

    ;~ ; Inform user of progress
    ;~ DetailPrint "Creating uninstaller..."

    ;~ ; Generate uninstaller
    ;~ WriteUninstaller "$INSTDIR\Uninstall.exe"

    ;~ ; Completion message
    ;~ DetailPrint "Installation completed successfully!"
;~ SectionEnd

;~ ; Uninstall Section
;~ Section "Uninstall"
    ;~ ; Display progress
    ;~ DetailPrint "Preparing to uninstall..."

    ;~ ; Remove desktop shortcut
    ;~ DetailPrint "Removing desktop shortcut..."
    ;~ Delete "$DESKTOP\SplashCaseCreator.lnk"

    ;~ ; Remove Start Menu folder and shortcuts
    ;~ DetailPrint "Removing Start Menu shortcuts..."
    ;~ Delete "$SMPROGRAMS\SplashCaseCreator\SplashCaseCreator.lnk"
    ;~ Delete "$SMPROGRAMS\SplashCaseCreator\Uninstall.lnk"
    ;~ Delete "$SMPROGRAMS\SplashCaseCreator\README.lnk"
    ;~ RMDir "$SMPROGRAMS\SplashCaseCreator"

    ;~ ; Remove installed files and directories
    ;~ DetailPrint "Removing installed files..."
    ;~ RMDir /r "$INSTDIR"

    ;~ ; Completion message
    ;~ DetailPrint "Uninstallation completed successfully!"
;~ SectionEnd

;~ ; Error handling for missing files
;~ !macro ErrorHandler
;~ Function .onError
    ;~ MessageBox MB_ICONERROR|MB_OK "An error occurred during the installation. Please try again."
    ;~ Quit
;~ FunctionEnd
;~ !macroend

;~ ; Define a custom uninstaller page
;~ Function un.onInit
    ;~ MessageBox MB_ICONQUESTION|MB_YESNO "Do you really want to uninstall SplashCaseCreator?" /SD IDYES IDNO EndAbort
    ;~ Return
;~ EndAbort:
    ;~ Quit
;~ FunctionEnd




!include "MUI2.nsh"

; Define Installer Name and Output
OutFile "SplashCaseCreatorSetup.exe"
InstallDir "$PROGRAMFILES\SplashCaseCreator"
RequestExecutionLevel admin

; Define branding and appearance
!define MUI_ABORTWARNING
!define MUI_ICON "../../Resources/Logos/simulitica_icon_logo.ico"
!define MUI_UNICON "../../Resources/Logos/simulitica_icon_logo.ico"

; Define finish page text
!define MUI_FINISHPAGE_TITLE "Installation Complete"
!define MUI_FINISHPAGE_TEXT "SplashCaseCreator has been successfully installed. Click 'Finish' to start the application."
!define MUI_FINISHPAGE_RUN "$INSTDIR\SplashCaseCreator.exe"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"

; Set installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Set uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language settings
!insertmacro MUI_LANGUAGE "English"

; Branding options
Caption "SplashCaseCreator Installer"
BrandingText "Powered by Simulitica Technologies"

; Install Section
Section "Install"
    ; Set installation directory
    SetOutPath "$INSTDIR"

    ; Display progress
    DetailPrint "Preparing installation..."

    ; Copy all files from the build directory
    DetailPrint "Copying application files..."
    File /r "dist\SplashCaseCreator\*.*"

    ; Add README file
    DetailPrint "Copying README file..."
    File "README.txt"

    ; Add license file
    DetailPrint "Copying LICENSE file..."
    File "LICENSE.txt"

    ; Create desktop shortcut
    DetailPrint "Creating desktop shortcut..."
    CreateShortcut "$DESKTOP\SplashCaseCreator.lnk" "$INSTDIR\SplashCaseCreator.exe" \
        "" "$INSTDIR\SplashCaseCreator.exe" 0

    ; Create Start Menu folder
    DetailPrint "Creating Start Menu folder..."
    CreateDirectory "$SMPROGRAMS\SplashCaseCreator"

    ; Create Start Menu shortcuts
    DetailPrint "Creating Start Menu shortcuts..."
    CreateShortcut "$SMPROGRAMS\SplashCaseCreator\SplashCaseCreator.lnk" "$INSTDIR\SplashCaseCreator.exe" \
        "" "$INSTDIR\SplashCaseCreator.exe" 0
    CreateShortcut "$SMPROGRAMS\SplashCaseCreator\Uninstall.lnk" "$INSTDIR\Uninstall.exe" \
        "" "$INSTDIR\Uninstall.exe" 0
    CreateShortcut "$SMPROGRAMS\SplashCaseCreator\README.lnk" "$INSTDIR\README.txt" \
        "" "$INSTDIR\README.txt" 0

    ; Inform user of progress
    DetailPrint "Creating uninstaller..."

    ; Generate uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Completion message
    DetailPrint "Installation completed successfully!"
SectionEnd

; Uninstall Section
Section "Uninstall"
    ; Display progress
    DetailPrint "Preparing to uninstall..."

    ; Remove desktop shortcut
    DetailPrint "Removing desktop shortcut..."
    Delete "$DESKTOP\SplashCaseCreator.lnk"

    ; Remove Start Menu folder and shortcuts
    DetailPrint "Removing Start Menu shortcuts..."
    Delete "$SMPROGRAMS\SplashCaseCreator\SplashCaseCreator.lnk"
    Delete "$SMPROGRAMS\SplashCaseCreator\Uninstall.lnk"
    Delete "$SMPROGRAMS\SplashCaseCreator\README.lnk"
    RMDir "$SMPROGRAMS\SplashCaseCreator"

    ; Remove installed files and directories
    DetailPrint "Removing installed files..."
    RMDir /r "$INSTDIR"

    ; Completion message
    DetailPrint "Uninstallation completed successfully!"
SectionEnd

; Error handling for missing files
!macro ErrorHandler
Function .onError
    MessageBox MB_ICONERROR|MB_OK "An error occurred during the installation. Please try again."
    Quit
FunctionEnd
!macroend

; Define a custom uninstaller page
Function un.onInit
    MessageBox MB_ICONQUESTION|MB_YESNO "Do you really want to uninstall SplashCaseCreator?" /SD IDYES IDNO EndAbort
    Return
EndAbort:
    Quit
FunctionEnd
