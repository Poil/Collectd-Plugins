<?php
header('Content-Type: application/json');
if(!$cache_info = @apc_cache_info()) {
die("No cache info available.");
}
$sma_info = apc_sma_info();
$mem_used = $sma_info['seg_size'] - $sma_info['avail_mem'];
echo '{'."\n";
echo '  "mem": {'."\n";
//echo '   "size:'.$sma_info['seg_size'].",\n";
echo '    "free": '.($sma_info['seg_size']-$mem_used).",\n";
echo '    "used": '.$mem_used."\n";
echo '  },'."\n";
echo '  "num": {'."\n";
echo '    "hits": '.$cache_info['num_hits'].",\n";
echo '    "misses": '.$cache_info['num_misses']."\n";
echo '  },'."\n";
echo '  "files": {'."\n";
echo '    "cached": '.count($cache_info['cache_list']).",\n";
echo '    "deleted": '.count($cache_info['deleted_list'])."\n";
echo '  }'."\n";
echo '}'."\n";
?>

