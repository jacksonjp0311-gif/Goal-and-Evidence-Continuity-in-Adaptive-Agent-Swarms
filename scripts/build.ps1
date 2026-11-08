# Rebuild the white paper from paper/whitepaper.md.
# Usage, from the repository root:
#   powershell -ExecutionPolicy Bypass -File scripts/build.ps1
# Requires Python 3, the packages in scripts/requirements.txt, and Microsoft Word.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

cmd /c "python -m pip install --user -r `"$Root\scripts\requirements.txt`""
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
python (Join-Path $Root "scripts\draw_figures.py")
python (Join-Path $Root "scripts\render_docx.py")

$docx = (Resolve-Path (Join-Path $Root "source\whitepaper.docx")).Path
$pdf = Join-Path $Root "paper\whitepaper.pdf"
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.Options.UpdateLinksAtOpen = $false
    $doc = $word.Documents.Open($docx, $false, $false, $false)
    # 17 is wdFormatPDF. SaveAs2 avoids the ExportAsFixedFormat dispatch hang.
    $null = $doc.SaveAs2($pdf, 17)
}
finally {
    if ($doc -ne $null) { $doc.Close($false) | Out-Null }
    if ($word -ne $null -and $word.Documents.Count -eq 0) { $word.Quit() | Out-Null }
}

python (Join-Path $Root "scripts\finish_pdf.py")
python (Join-Path $Root "scripts\check_publication.py")
