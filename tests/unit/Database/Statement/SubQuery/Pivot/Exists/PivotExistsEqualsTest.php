<?php


use App\Database\Statement\SubQuery\Pivot\Exists\PivotExistsEquals;

class PivotExistsEqualsTest extends TestCase
{


    /**
     * @test
     */
    public function returns_correct_statement()
    {
        $query = new PivotExistsEquals('author_book','book_id','author_id','books.id');

        $sql = "SELECT `book_id` FROM `author_book` WHERE `author_id` = ? AND `book_id` = `books`.`id`";

        $this->assertEquals($this->trimWhiteSpace($sql),$this->trimWhiteSpace($query->query()),"PivotExistsEquals::query() returned invaild statement");

    }

}