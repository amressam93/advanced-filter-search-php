<?php


namespace App\Search\Filter\Book;

use App\Search\Filter\FilterContract;
use App\Database\Concat\ConcatAnd;
use App\Database\Filter;
use App\Database\Statement\Query\Equals;


class Year implements FilterContract
{

    /** Get Filter
     * @return Filter
     */
    public static function filter()
    {

        return new Filter(
            [
                new Equals('books.year')
            ],
            new ConcatAnd()
        );


    }
}