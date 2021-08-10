<?php

use App\Database\Database;
use App\Database\DatabaseManager;
use App\Migration\MigrationManager;
use App\Migration\Model\Migration;
use App\Model\Book;


class DatabaseTest extends TestCase
{

    use BookStore;

    /**
     * @var Database
     */
    private $db;



    protected function setUp(): void
    {
        parent::setUp();
        $this->db = DatabaseManager::make();

        (new MigrationManager(new Migration($this->db)))->up();
    }



    protected function tearDown(): void
    {
        parent::tearDown();
        (new MigrationManager(new Migration($this->db)))->down();
    }


    /**
     * @test
     */
    public function excutes_simple_query()
    {

        $result = $this->db->execute("SELECT MAX(1, 10)");
        $this->assertEquals(10,$result,"Query Returned incorrect Max Value");
    }

    /**
     * @test
     */
    public function inserts_new_record()
    {
        $results = $this->addBook();
        $this->assertTrue($results,"The Insert Statment Failed");
    }


    /**
     * @test
     */
    public function updates_record()
    {
        $this->addBook(['isbn' => 123]);
        $update = $this->db->update(
            'books',
            [
               'isbn' => 456
            ],
            $this->lastInsertId

        );

        $this->assertTrue($update,"The Update Statement Failed");

        $book = $this->db->fetchObject(
            "SELECT * FROM `books` WHERE `id` = ?",
            $this->lastInsertId
        );

        $this->assertEquals(456,$book->isbn,'ISBN was Not Updated');

    }




    /**
     * @test
     */

    public function fetch_object_returns_std_class_instance()
    {
        $this->addBook(['title' => 'Book Of Jungle']);

        $book = $this->db->fetchObject("SELECT * FROM `books` WHERE `id` = ?",$this->lastInsertId);

        $this->assertInstanceOf(stdClass::class,$book,"Call To fetchObject Did Not Return stdClass Instance");

        $this->assertEquals('Book Of Jungle',$book->title,"stdClass instance does not return correct title");

    }



    /**
     * @test
     */

    public function fetch_object_returns_book_instance()
    {
        $this->addBook(['title' => 'Book Of Jungle']);

        $book = $this->db->fetchObject("SELECT * FROM `books` WHERE `id` = ?",$this->lastInsertId,Book::class);

        $this->assertInstanceOf(Book::class,$book,"Call To fetchObject Did Not Return Book Instance");

        $this->assertEquals('Book Of Jungle',$book->title,"Book instance does not return correct title");
    }



    /**
     * @test
     */

    public function removes_record()
    {
        $this->addBook(['title' => 'Book Of Jungle']);

        $book = $this->db->fetchObject("SELECT * FROM `books` WHERE `id` = ?",$this->lastInsertId);

        $this->assertNotEmpty($book,"Book Record Not Found");

        $this->assertEquals('Book Of Jungle',$book->title,'Book Record Title does Not Match');

        $this->db->delete('books',$book->id);

        $book = $this->db->fetchObject("SELECT * FROM `books` WHERE `id` = ?",$this->lastInsertId);

        $this->assertFalse($book,'Book Record was Found');
    }




    /**
     * @test
     */

    public function count_returns_correct_number_of_records()

    {
        $this->addBook();
        $this->addBook();
        $this->addBook();

        $this->assertEquals(3,$this->db->count('books'),"Books Table Did Not Return 3 Records");
        $this->assertEquals(2,$this->db->count('books',' WHERE `id` < 3' ),"Books Table Did Not Return 2 Records with id less than 3");
    }




    /**
     * @test
     */


    public function fetch_objects_returns_the_correct_number_of_records()

    {
        $this->addBook(['title' => 'Book Of Jungle']);
        $this->addBook(['title' => 'Game Of Thrones']);

        $books = $this->db->fetchObjects("SELECT * FROM `books`");

        $this->assertCount(2,$books,"Fetch Objects count did not return 2 records");

    }



    /**
     * @test
     */

    public function fetch_objects_returns_array_of_std_class_objects()

    {
        $this->addBook(['title' => 'Book Of Jungle']);
        $this->addBook(['title' => 'Game Of Thrones']);

        $books = $this->db->fetchObjects("SELECT * FROM `books`");

        $this->assertInstanceOf(stdClass::class,$books[0],"First Item does not apper to be a stdclass instance");
        $this->assertInstanceOf(stdClass::class,$books[1],"second Item does not apper to be a stdclass instance");


    }


    /**
     * @test
     */

    public function fetch_objects_returns_array_of_book_objects()
    {
        $this->addBook(['title' => 'Book Of Jungle']);
        $this->addBook(['title' => 'Game Of Thrones']);

        $books = $this->db->fetchObjects("SELECT * FROM `books`",null,Book::class);

        $this->assertInstanceOf(Book::class,$books[0],"First Item does not apper to be a Book class instance");
        $this->assertInstanceOf(Book::class,$books[1],"second Item does not apper to be a Book class instance");
    }



}