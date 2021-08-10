<?php


use App\Database\Concat\ConcatAnd;

class ConcatAndTest extends TestCase
{


    /**
     * @var ConcatAnd
     */
    private $concat;


    /**
     * Set up before each test.
     *
     * @return void
     */
    protected function setUp(): void
    {
        parent::setUp();

        $this->concat = new ConcatAnd();
    }


    /**
     * @test
     */
    public function concat_and_with_concat()
    {
        $this->assertEquals("AND `books`.`id` = ?",$this->concat->concat("`books`.`id` = ?"),"Invaild result for ConcatAnd::concat");

    }





    /**
     * @test
     */
    public function concat_and_with_first_concat()
    {
        $this->assertEquals("`books`.`id` = ?",$this->concat->concatFirst("`books`.`id` = ?"),"Invaild result for ConcatAnd::concatFirst");
    }






}