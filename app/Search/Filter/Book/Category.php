<?php


namespace App\Search\Filter\Book;


use App\Search\Filter\FilterContract;
use App\Database\Filter;
use App\Database\Concat\ConcatAnd;
use App\Database\Statement\Query\Equals;


class Category implements FilterContract
{

    /**
     * Get Filter.
     * @return Filter
     */
    public static function filter()
    {
       return new Filter(
           [
               new Equals('books.category_id')
           ],
           new ConcatAnd()
       );
    }
}