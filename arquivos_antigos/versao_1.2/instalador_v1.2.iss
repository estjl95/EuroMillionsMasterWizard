[Setup]
AppName=EuroMillions Master Wizard 
AppVersion=1.2
AppPublisher=José Estácio
AppComments=Programa concebido para prever números prováveis com base em estatísticas reais do EuroMilhões, utilizando métodos matemáticos para aumentar eficazmente as probabilidades de ganhar o jackpot.
AppCopyright=© 2025 José Estácio
DefaultDirName={pf}\EuroMillionsMasterWizard v1.2
DefaultGroupName=EuroMillionsMasterWizard v1.2
OutputDir={userdocs}\EuroMillions Master Wizard v1.2
OutputBaseFilename=Setup
SetupIconFile=icone.ico
Compression=lzma
SolidCompression=yes
LicenseFile=LICENSE.txt
UninstallDisplayName=EuroMillions Master Wizard v1.2
UninstallDisplayIcon={app}\icone.ico
UninstallFilesDir={app}\dados

[Files]
Source: "dist\EuroMillionsMasterWizard.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dados\resultados_euromilhoes.xlsx"; DestDir: "{app}\dados"; Flags: ignoreversion
Source: "splash.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\msgbox.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\EuroMillionsMasterWizard"; Filename: "{app}\EuroMillionsMasterWizard.exe"
Name: "{userdesktop}\EuroMillions Master Wizard"; Filename: "{app}\EuroMillionsMasterWizard.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho no ambiente de trabalho"; GroupDescription: "Opções adicionais:"

[Run]
Filename: "{app}\EuroMillionsMasterWizard.exe"; Description: "Executar após instalação"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\dados"

[UninstallRun]
Filename: "{app}\msgbox.exe"; Flags: runhidden