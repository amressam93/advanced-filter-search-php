<?php


namespace App\Database\Concat;


class ConcatOr implements ConcatContract
{


    /**
     * Concat statement.
     *
     * @param string $statement
     * @return string
     */

    public static function concat($statement)
    {
        return "OR {$statement}";
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