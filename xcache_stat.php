<?php
header('Content-Type: application/json');
function _T($str) {
	if (isset($GLOBALS['strings'][$str])) {
		return $GLOBALS['strings'][$str];
	}
	if (!empty($GLOBALS['config']['show_todo_strings'])) {
		return '<span style="color:red">' . $str . '</span>|';
	}
	return $str;
}

function getCacheInfos() {
	static $cacheInfos;
	if (isset($cacheInfos)) {
		return $cacheInfos;
	}

	$phpCacheCount = xcache_count(XC_TYPE_PHP);
	$varCacheCount = xcache_count(XC_TYPE_VAR);

	$cacheInfos = array();
	$total = array();
	global $maxHitsByHour;
	$maxHitsByHour = array(0, 0);
	for ($i = 0; $i < $phpCacheCount; $i ++) {
		$data = xcache_info(XC_TYPE_PHP, $i);
		if ($_GET['do'] === 'listphp') {
			$data += xcache_list(XC_TYPE_PHP, $i);
		}
		$data['type'] = XC_TYPE_PHP;
		$data['cache_name'] = "php#$i";
		$data['cacheid'] = $i;
		$cacheInfos[] = $data;
		$maxHitsByHour[XC_TYPE_PHP] = max($maxHitsByHour[XC_TYPE_PHP], max($data['hits_by_hour']));
		if ($phpCacheCount >= 2) {
			calc_total($total, $data);
		}
	}

	if ($phpCacheCount >= 2) {
		$total['type'] = XC_TYPE_PHP;
		$total['cache_name'] = _T('Total');
		$total['cacheid'] = -1;
		$total['gc'] = null;
		$total['istotal'] = true;
		unset($total['compiling']);
		$cacheInfos[] = $total;
	}

	$total = array();
	for ($i = 0; $i < $varCacheCount; $i ++) {
		$data = xcache_info(XC_TYPE_VAR, $i);
		if ($_GET['do'] === 'listvar') {
			$data += xcache_list(XC_TYPE_VAR, $i);
		}
		$data['type'] = XC_TYPE_VAR;
		$data['cache_name'] = "var#$i";
		$data['cacheid'] = $i;
		$cacheInfos[] = $data;
		$maxHitsByHour[XC_TYPE_VAR] = max($maxHitsByHour[XC_TYPE_VAR], max($data['hits_by_hour']));
		if ($varCacheCount >= 2) {
			calc_total($total, $data);
		}
	}

	if ($varCacheCount >= 2) {
		$total['type'] = XC_TYPE_VAR;
		$total['cache_name'] = _T('Total');
		$total['cacheid'] = -1;
		$total['gc'] = null;
		$total['istotal'] = true;
		$cacheInfos[] = $total;
	}
	return $cacheInfos;
}

function calc_total(&$total, $data) {
	foreach ($data as $k => $v) {
		switch ($k) {
		case 'type':
		case 'cache_name':
		case 'cacheid':
		case 'free_blocks':
			continue 2;
		}
		if (!isset($total[$k])) {
			$total[$k] = $v;
		}
		else {
			switch ($k) {
			case 'hits_by_hour':
			case 'hits_by_second':
				foreach ($data[$k] as $kk => $vv) {
					$total[$k][$kk] += $vv;
				}
				break;

			default:
				$total[$k] += $v;
			}
		}
	}
}

echo json_encode(getCacheInfos());
