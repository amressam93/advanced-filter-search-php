<?php


use App\Database\Concat\ConcatOr;

class ConcatOrTest extends TestCase
{


    /**
     * @var ConcatOr
     */
    private $concat;


    /**
     * set up before each test.
     * @return void
     */
    protected function setUp(): void
    {
        parent::setUp();

        $this->concat = new ConcatOr();
    }


    /**
     * @test
     */
    public function concat_or_with_concat()
    {
        $this->assertEquals("OR `books`.`id` = ?",$this->concat->concat("`books`.`id` = ?"),"Invaild result for ConcatOr::concat");
    }






    /**
     * @test
     */
    public function concat_or_with_concat_first()
    {
        $this->assertEquals("`books`.`id` = ?",$this->concat->concatFirst("`books`.`id` = ?"),"Invaild result for ConcatOr::concatFirst");
    }





}