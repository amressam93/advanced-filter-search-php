<?php


namespace App\Database\Concat;


class ConcatOrWrap implements ConcatContract
{

    /**
     * @param string $statement
     * @return mixed
     */
    public static function concat($statement)
    {
        return "OR ({$statement})";
    }




    /**
     * @param string $statement
     * @return mixed
     */
    public static function concatFirst($statement)
    {
        return "({$statement})";
    }



}