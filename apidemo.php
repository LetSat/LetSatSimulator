<?php
# LatSat Rendering Server
# 13 Feb 2018 - v0.1 - Initial implementation with VirtualGL
# v1.0
# Chandler Griscom
function random_string($length) {
    $key = '';
    $keys = array_merge(range(0, 9), range('a', 'z'));

    for ($i = 0; $i < $length; $i++) {
        $key .= $keys[array_rand($keys)];
    }

    return $key;
}

if(isset($_GET["submit"])) {
    
    $outfile = "/tmp/".random_string(30).".png";
    $call = "DISPLAY=:0 ./openGLRender.py";
    $call = $call." ".$_GET['lat'];
    $call = $call." ".$_GET['long'];
    $call = $call." ".$_GET['alt'];
    $call = $call." ".$_GET['texture'];
    $call = $call." ".$outfile;
    if (isset($_GET['size'])) $call = $call." --size ".$_GET['size'];
    if (isset($_GET['fov'])) $call = $call." --fov ".$_GET['fov'];
    $call = $call." 2>&1";
    $output = shell_exec($call);

    if ($output.trim() === "") {
        header('Content-Type: image/png');
        header('Content-Length: ' . filesize($outfile)); 
        readfile($outfile);
    } else {
        header('Content-type: text/plain');
        echo $call;
        echo "\n";
        echo $output;
    }
    unlink($outfile);
} else {
?>

<!DOCTYPE html>
<html>
<head>

</head>
<body>
    <pre>
<?php
    echo shell_exec("./openGLRender.py -h");
?>
    </pre>
    <form action="" method="get">
    <table>
    <tr><td>lat:</td><td><input type="text" name="lat" value=""></td></tr>
    <tr><td>long:</td><td><input type="text" name="long" value=""></td></tr>
    <tr><td>alt:</td><td><input type="text" name="alt" value=""></td></tr>
    <tr><td>texture:</td><td><select name="texture"><?php    
$texdir="build_textures/";
if ($handle = opendir($texdir)) {
    while (false !== ($file = readdir($handle))) {
        if ('.' === $file) continue;
        if ('..' === $file) continue;
        echo "<option value='$texdir$file'>$texdir$file</option>";
    }
    closedir($handle);
}
?></select></td></tr>
    <tr><td>size:</td><td><input type="text" name="size" value="1024"></td></tr>
    <tr><td>fov:</td><td><input type="text" name="fov" value="141"></td></tr>
    </table>

    <input type="submit" value="Download" name="submit">
    </form>
</body>
</html>

<?php
}
?>
