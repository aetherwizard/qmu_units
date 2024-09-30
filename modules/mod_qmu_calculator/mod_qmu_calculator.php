<?php
defined('_JEXEC') or die;

use Joomla\CMS\Helper\ModuleHelper;

require_once __DIR__ . '/helper.php';

$helper = new ModQmuCalculatorHelper();
$units = $helper->getUnits();

require ModuleHelper::getLayoutPath('mod_qmu_calculator', 'default');
