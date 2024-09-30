<?php
defined('_JEXEC') or die;

class ModQmuCalculatorHelper
{
    public function getUnits()
    {
        // Implement logic to return QMU units
        // This might involve reading from a JSON file or database
        return [
            'me' => ['name' => 'Electron mass', 'symbol' => 'me'],
            'λC' => ['name' => 'Compton wavelength', 'symbol' => 'λC'],
            // ... add all other units
        ];
    }
}
