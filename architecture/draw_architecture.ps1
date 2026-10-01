Add-Type -AssemblyName System.Drawing
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $scriptDir) { $scriptDir = Join-Path (Get-Location) 'outputs\Azure-LLMOps-Support-Ticket-Assistant\architecture' }
$out = Join-Path $scriptDir 'azure_llmops_architecture.png'
$bmp = [System.Drawing.Bitmap]::new(1800, 1050)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$bg = [System.Drawing.Color]::FromArgb(14, 20, 34)
$g.Clear($bg)
$fontTitle = [System.Drawing.Font]::new('Segoe UI', 28, [System.Drawing.FontStyle]::Bold)
$fontSub = [System.Drawing.Font]::new('Segoe UI', 12)
$fontHead = [System.Drawing.Font]::new('Segoe UI', 15, [System.Drawing.FontStyle]::Bold)
$fontBody = [System.Drawing.Font]::new('Segoe UI', 11)
$white = [System.Drawing.Brushes]::White
$muted = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(173, 188, 209))
$g.DrawString('Azure LLMOps Support Ticket Assistant', $fontTitle, $white, 54, 34)
$g.DrawString('Planned architecture | Local/offline demonstration path | Cloud deployment not provisioned', $fontSub, $muted, 58, 82)

function Draw-Card([int]$x,[int]$y,[int]$w,[int]$h,[string]$title,[string]$body,[System.Drawing.Color]$accent) {
  $body = $body.Replace('\n', [Environment]::NewLine)
  $fill = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(31, 43, 64))
  $pen = [System.Drawing.Pen]::new($accent, 3)
  $g.FillRectangle($fill, $x, $y, $w, $h)
  $g.DrawRectangle($pen, $x, $y, $w, $h)
  $g.DrawString($title, $fontHead, $white, [System.Drawing.RectangleF]::new($x+16,$y+14,$w-32,28))
  $fmt = [System.Drawing.StringFormat]::new()
  $fmt.Trimming = [System.Drawing.StringTrimming]::Word
  $g.DrawString($body, $fontBody, $muted, [System.Drawing.RectangleF]::new($x+16,$y+50,$w-32,$h-58), $fmt)
  $fmt.Dispose(); $pen.Dispose(); $fill.Dispose()
}
function Draw-Arrow([int]$x1,[int]$y1,[int]$x2,[int]$y2,[bool]$dashed=$false) {
  $pen = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(105, 190, 255), 3)
  $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
  if ($dashed) { $pen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash }
  $g.DrawLine($pen,$x1,$y1,$x2,$y2); $pen.Dispose()
}
$blue = [System.Drawing.Color]::FromArgb(83, 173, 255)
$green = [System.Drawing.Color]::FromArgb(86, 208, 158)
$purple = [System.Drawing.Color]::FromArgb(179, 131, 255)
$orange = [System.Drawing.Color]::FromArgb(255, 177, 91)
$red = [System.Drawing.Color]::FromArgb(255, 117, 125)

Draw-Card 55 165 245 150 'Blob CSV' 'Existing private storage\n12,000 support tickets' $blue
Draw-Card 350 165 245 150 'Ingestion' 'DefaultAzureCredential\nNo storage keys in code' $green
Draw-Card 645 165 245 150 'Preprocess' 'Validate / redact / split\nPandas quality checks' $green
Draw-Card 940 165 245 150 'FastAPI' 'Single / batch routes\nPydantic JSON contract' $purple
Draw-Card 1235 165 245 150 'Ticket processor' 'Versioned prompts\nRetries / safe errors' $purple
Draw-Card 1530 165 245 150 'Model choice' 'Offline rules now\nAzure OpenAI optional' $orange
Draw-Arrow 300 240 350 240; Draw-Arrow 595 240 645 240; Draw-Arrow 890 240 940 240; Draw-Arrow 1185 240 1235 240; Draw-Arrow 1480 240 1530 240

Draw-Card 1200 430 270 145 'Offline baseline' 'Deterministic rules\nNo token or Azure charge' $green
Draw-Card 1510 430 270 145 'Azure OpenAI' 'Metered model endpoint\nDeploy only after approval' $red
Draw-Card 890 430 270 145 'Validated JSON' 'Category / priority\nResolution suggestion' $blue
Draw-Arrow 1575 315 1360 420; Draw-Arrow 1710 315 1650 420
Draw-Arrow 1200 502 1165 502; Draw-Arrow 1645 575 1645 630; Draw-Arrow 1645 630 1025 630; Draw-Arrow 1025 630 1025 575

Draw-Card 630 430 220 145 'Evaluation' 'Held-out split\nMetrics, no fake scores' $orange
Draw-Card 350 430 220 145 'Experiment log' 'Local JSONL\nPrompt/model versions' $green
Draw-Arrow 760 315 740 420; Draw-Arrow 630 500 575 500
Draw-Card 55 430 235 145 'GitHub Actions' 'Compile / test\nBuild image only' $purple
Draw-Card 55 700 235 145 'Container image' 'Docker build\nHealth check' $blue
Draw-Card 350 700 250 145 'Azure Container Apps' 'Optional Consumption\nScale to zero' $orange
Draw-Card 670 700 260 145 'App Insights' 'Optional monitoring\nRedacted telemetry only' $red
Draw-Arrow 170 575 170 690; Draw-Arrow 290 775 350 775; Draw-Arrow 600 775 670 775 $true
Draw-Arrow 1065 315 1065 420

$g.DrawString('Approval gate: check region + current price, estimate monthly use, confirm acceptable budget before provisioning.', $fontSub, $muted, 56, 930)
$fontSub.Dispose(); $fontHead.Dispose(); $fontBody.Dispose(); $fontTitle.Dispose(); $muted.Dispose(); $g.Dispose(); $bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
Write-Output $out
