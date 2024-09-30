<?php
defined('_JEXEC') or die;
?>

<div id="qmu-calculator">
    <h3>QMU Calculator</h3>
    <select id="unit1">
        <?php foreach ($units as $symbol => $unit): ?>
            <option value="<?php echo $symbol; ?>"><?php echo $unit['name']; ?></option>
        <?php endforeach; ?>
    </select>
    <input type="number" id="value1">
    
    <select id="operation">
        <option value="*">*</option>
        <option value="/">/</option>
        <option value="+">+</option>
        <option value="-">-</option>
    </select>
    
    <select id="unit2">
        <?php foreach ($units as $symbol => $unit): ?>
            <option value="<?php echo $symbol; ?>"><?php echo $unit['name']; ?></option>
        <?php endforeach; ?>
    </select>
    <input type="number" id="value2">
    
    <button id="calculate">Calculate</button>
    
    <div id="result"></div>
</div>

<script src="modules/mod_qmu_calculator/assets/js/qmu_calculator.js"></script>
