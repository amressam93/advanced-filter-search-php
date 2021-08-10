<?php


class SelectPaginationViewTest extends PaginationCase
{


    /**
     * @test
     */
    public function can_call_limit_method()
    {
        $pagination = $this->selectPagintionView(10,10);

        $this->assertEquals(10,$pagination->limit());

    }






    /**
     * @test
     */
    public function can_call_offset_method()
    {
        $pagination = $this->selectPagintionView(10,10);

        $this->assertEquals(0,$pagination->offset());

    }



    /**
     * @test
     */
    public function returns_empty_string_without_minimum_number_of_records()
    {
        $pagination = $this->selectPagintionView(10,10);
        $this->assertEquals('',$pagination->get());
    }







    /**
     * @test
     */
    public function returns_pagination_with_over_minimum_number_of_records()
    {
        $pagination = $this->selectPagintionView(10,9);
        $this->assertNotEquals('',$pagination->get());
    }










    /**
     * @test
     */
    public function returns_correct_html_structure_on_the_first_page()
    {
        $pagination = $this->selectPagintionView(100,10);



        $this->assertStringNotContainsString($this->button(['page' => 1]),$pagination->get());

        $this->assertStringContainsString($this->button(['page' => 2],true),$pagination->get());

        $this->assertStringContainsString($this->option(['page' => 1],true,true),$pagination->get());

        $this->assertStringContainsString($this->option(['page' => 2],true),$pagination->get());
    }










    /**
     * @test
     */

    public function returns_correct_html_structure_on_the_last_page()

    {

        $_GET['page'] = 10;
        $pagination = $this->selectPagintionView(100,10);

        $this->assertStringContainsString($this->button(['page' => 9],true),$pagination->get());

        $this->assertStringNotContainsString($this->urlWithQuery(['page' => 11],true),$pagination->get());


        $this->assertStringContainsString($this->option(['page' => 10],true,true),$pagination->get());

        $this->assertStringContainsString($this->option(['page' => 9],true,false),$pagination->get());

    }






    /**
     * @test
     */

    public function returns_correct_html_structure_of_the_page_between_first_and_last()

    {

        $_GET['page'] = 5;

        $pagination = $this->selectPagintionView(100,10);

        $this->assertStringContainsString($this->button(['page' => 4],true),$pagination->get());




        $this->assertStringContainsString($this->option(['page' => 5],true,true),$pagination->get());

        $this->assertStringContainsString($this->option(['page' => 4],true),$pagination->get());

        $this->assertStringContainsString($this->option(['page' => 6],true),$pagination->get());

        $this->assertStringContainsString($this->button(['page' => 6],true),$pagination->get());


        $this->assertStringNotContainsString($this->urlWithQuery(['page' => 11],true),$pagination->get());

    }


}