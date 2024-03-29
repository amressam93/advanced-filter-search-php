<?php


namespace App\Database\Concat;


class ConcatAnd implements ConcatContract
{


    /**
     * Concat statement.
     *
     * @param string $statement
     * @return string
     */

    public static function concat($statement)
    {
        return "AND {$statement}";
    }





    /**
     * Concat First Statement
     *
     * @param string $statement
     * @return string
     */

    public static function concatFirst($statement)
    {
        return $statement;
    }




}