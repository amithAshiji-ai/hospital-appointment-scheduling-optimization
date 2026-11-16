Add-Type -AssemblyName System.Drawing

$outputDirectory = Join-Path $PSScriptRoot "..\screenshots"
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
$outputPath = Join-Path $outputDirectory "results_comparison.png"

$image = New-Object System.Drawing.Bitmap 1000, 560
$graphics = [System.Drawing.Graphics]::FromImage($image)
$graphics.Clear([System.Drawing.Color]::White)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias

$titleFont = New-Object System.Drawing.Font "Arial", 24, ([System.Drawing.FontStyle]::Bold)
$labelFont = New-Object System.Drawing.Font "Arial", 15
$valueFont = New-Object System.Drawing.Font "Arial", 15, ([System.Drawing.FontStyle]::Bold)
$blue = [System.Drawing.Color]::FromArgb(49, 130, 189)
$lightBlue = [System.Drawing.Color]::FromArgb(158, 202, 225)
$dark = [System.Drawing.Color]::FromArgb(31, 41, 55)

$graphics.DrawString("Hospital Appointment Scheduling Results", $titleFont, (New-Object System.Drawing.SolidBrush $dark), 240, 30)

$columns = @(
    @{ Title = "Total Delay"; Initial = "8 slots"; Optimized = "8 slots"; X = 80 },
    @{ Title = "Preference Deviation"; Initial = "8"; Optimized = "6"; X = 390 },
    @{ Title = "Appointment Conflicts"; Initial = "0"; Optimized = "0"; X = 700 }
)

foreach ($column in $columns) {
    $graphics.FillRectangle((New-Object System.Drawing.SolidBrush $lightBlue), $column.X, 180, 110, 170)
    $graphics.FillRectangle((New-Object System.Drawing.SolidBrush $blue), ($column.X + 125), 180, 110, 170)
    $graphics.DrawString($column.Initial, $valueFont, (New-Object System.Drawing.SolidBrush $dark), ($column.X + 29), 245)
    $graphics.DrawString($column.Optimized, $valueFont, (New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::White)), ($column.X + 149), 245)
    $graphics.DrawString($column.Title, $labelFont, (New-Object System.Drawing.SolidBrush $dark), $column.X, 385)
}

$graphics.FillRectangle((New-Object System.Drawing.SolidBrush $lightBlue), 300, 465, 18, 18)
$graphics.DrawString("Initial Schedule", $labelFont, (New-Object System.Drawing.SolidBrush $dark), 325, 465)
$graphics.FillRectangle((New-Object System.Drawing.SolidBrush $blue), 530, 465, 18, 18)
$graphics.DrawString("GA Optimized Schedule", $labelFont, (New-Object System.Drawing.SolidBrush $dark), 555, 465)

$image.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$image.Dispose()
