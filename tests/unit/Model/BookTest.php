<?php

use App\Model\Author;
use App\Model\AuthorBook;
use App\Model\Book;
use App\Model\BookCover;
use App\Model\BookLanguage;
use App\Model\BookLocation;
use App\Model\Cover;
use App\Model\Language;
use App\Model\Location;
use App\Model\Model;


class BookTest extends ModelCase
{

    use ModelData;


    /**
     * @var Book
     */
    protected $book;


    /**
     * set up before each test.
     *
     * @return void
     */
    protected function setUp(): void
    {
        parent::setUp();

        $this->book = new Book;
    }


    /**
     * add new Book Record.
     *
     * @param array $user_data
     * @return Model
     * @throws Exception
     */
    public function addBook(array $user_data = [])
    {
        return $this->book->create($this->bookData($user_data));
    }





    /**
     * @test
     */

    public function can_insert_new_book()
    {
        $this->assertTrue($this->book->insert($this->bookData()));
    }



    /**
     * @test
     */

    public function can_create_new_book()
    {
        $newbook = $this->addBook(['title' => 'room with a window']);

        $this->assertInstanceOf(Book::class,$newbook,"Book::class did not return Book instance");

        $book = $this->book->find($newbook->id);

        $this->assertEquals('room with a window',$book->title,"Book was not created");

    }





    /**
     * @test
     */

    public function can_update_book()
    {
        $book = $this->addBook(['title' => 'room with a window']);

        $this->assertEquals('room with a window',$book->title,'book was not added before the update');

        $updatedBook = $this->book->update(['title' => 'new title'],$book->id);

        $this->assertEquals('new title',$updatedBook->title,"book was not updated");

    }




    /**
     * @test
     */


    public function can_remove_book()
    {
        $book  = $this->addBook();
        $books = $this->book->all();

        $this->assertCount(1,$books,"number of books does not match 1");

        $book->delete($book->id);

        $books = $this->book->all();

        $this->assertCount(0,$books,"number of book does not match 0");

    }







    /**
     * @test
     */

    public function books_collection_is_empty()
    {

        $books = $this->book->all();

        $this->assertEmpty($books,"Book::all returned not empty");

    }






    /**
     * @test
     */

    public function books_collection_is_not_empty()
    {
        $this->addBook();

        $books = $this->book->books();

        $this->assertCount(1,$books,"Book::books count is incorrect");
    }





    /**
     * @test
     */

    public function books_collection_is_ordered_by_title()
    {
        $this->addBook(['title' => 'Game of thrones']);
        $this->addBook(['title' => 'Another day in paradise']);

        $books = $this->book->books();

        $this->assertCount(2,$books,"Book::books count does not match 2");

        $this->assertEquals('Another day in paradise',$books[0]->title,"Book::books[0] order is incorrect");
        $this->assertEquals('Game of thrones',$books[1]->title,"Book::books[1] order is incorrect");
    }






    /**
     * @test
     */

    public function returns_formatted_price()
    {
        $book = $this->addBook(['price' => 5.6]);

        $this->assertEquals('€5.60',$book->price(),"price was not formatted correctly");
    }




    /**
     * @test
     */

    public function returns_concatenated_list_of_associated_authors()
    {
        $book = $this->addBook();

        $authorOne = (new Author)->create($this->lookupData(['name' => 'Ernest Hemingway']));
        $authorTwo = (new Author)->create($this->lookupData(['name' => 'Franz Kafka']));

        $authorBook = new AuthorBook;

        $authorBook->insert([
            'author_id' => $authorOne->id,
            'book_id'   => $book->id
        ]);


        $authorBook->insert([
            'author_id' => $authorTwo->id,
            'book_id'   => $book->id
        ]);


        $book = $book->find($book->id);

        $this->assertEquals('Ernest Hemingway, Franz Kafka',$book->authors(),"Invaild author Formatting");

        $this->assertEquals('Ernest Hemingway|Franz Kafka',$book->authors("|"),"Invaild author Formatting");


    }






    /**
     * @test
     */

    public function returns_concatenated_list_of_associated_languages()
    {
        $book = $this->addBook();

        $english = (new Language)->create($this->lookupData(['name' => 'English']));
        $french = (new Language)->create($this->lookupData(['name' => 'French']));

        $bookLanguage = new BookLanguage;

        $bookLanguage->insert([
            'language_id' => $english->id,
            'book_id'   => $book->id
        ]);


        $bookLanguage->insert([
            'language_id' => $french->id,
            'book_id'   => $book->id
        ]);


        $book = $book->find($book->id);

        $this->assertEquals('English, French',$book->languages(),"Invaild language Formatting");

        $this->assertEquals('English|French',$book->languages("|"),"Invaild language Formatting");


    }







    /**
     * @test
     */

    public function returns_concatenated_list_of_associated_locations()
    {
        $book = $this->addBook();

        $london = (new Location)->create($this->lookupData(['name' => 'London']));
        $paris = (new Location)->create($this->lookupData(['name' => 'Paris']));

        $bookLocation = new BookLocation;

        $bookLocation->insert([
            'location_id' => $london->id,
            'book_id'   => $book->id
        ]);


        $bookLocation->insert([
            'location_id' => $paris->id,
            'book_id'   => $book->id
        ]);


        $book = $book->find($book->id);

        $this->assertEquals('London, Paris',$book->locations(),"Invaild location Formatting");

        $this->assertEquals('London|Paris',$book->locations("|"),"Invaild location Formatting");


    }






    /**
     * @test
     */

    public function returns_concatenated_list_of_associated_covers()
    {
        $book = $this->addBook();

        $hard = (new Cover)->create($this->lookupData(['name' => 'Hard']));
        $soft = (new Cover)->create($this->lookupData(['name' => 'Soft']));

        $bookCover = new BookCover;

        $bookCover->insert([
            'cover_id' => $hard->id,
            'book_id'   => $book->id
        ]);


        $bookCover->insert([
            'cover_id' => $soft->id,
            'book_id'   => $book->id
        ]);


        $book = $book->find($book->id);

        $this->assertEquals('Hard, Soft',$book->covers(),"Invaild cover Formatting");

        $this->assertEquals('Hard|Soft',$book->covers("|"),"Invaild cover Formatting");


    }



}