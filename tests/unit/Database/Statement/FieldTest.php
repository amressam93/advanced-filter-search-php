<?php


use App\Database\Statement\Field;

class FieldTest extends TestCase
{


    /**
     * @test
     */
    public function returns_formatted_field_name()
    {
        $this->assertEquals("`name`",Field::fieldName("name"),"Incorrectly Formatted name");

        $this->assertEquals("`books`.`id`",Field::fieldName("books.id"),"Incorrectly Formatted `books`.`id`");

        $this->assertEquals("`books`.`first.name`",Field::fieldName("books.first.name"),"Incorrectly Formatted `books`.`first.name`");

    }



}