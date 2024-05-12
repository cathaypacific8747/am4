<?php
$matrix = array();

$xStart = 36;
$xEnd = 181;
$yStart = 182;
$yEnd = 301;

for ($x = $xStart; $x < $xEnd; $x++) {
    for ($y = $yStart; $y < $yEnd; $y++) {
        srand($x * $y);
        $matrix[$x][$y] = rand(600, 900);
    }
}

$fp = fopen('.rand.csv', 'w');

foreach ($matrix as $row) {
    fputcsv($fp, $row);
}

fclose($fp);
?>