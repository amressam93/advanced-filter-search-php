<?php


use App\Container;
use App\Database\DatabaseManager;
use App\Migration\MigrationManager;
use App\Migration\Model\Migration;

abstract class ModelCase extends TestCase
{


    /**
     * Migrate Database.
     *
     * @return void
     * @throws Exception
     */
    protected function migrate()
    {
        Container::bind([
            'db' => DatabaseManager::make()
        ]);

        (new MigrationManager(new Migration(Container::get('db'))))->up();

    }


    /**
     * set up before each test.
     *
     * @return void
     * @throws Exception
     */
    protected function setUp() :void
    {
        parent::setUp();
        $this->migrate();
    }


    /**
     * clean up after each test.
     *
     * @return void
     * @throws Exception
     */
    protected function tearDown(): void
    {
        parent::tearDown();
        (new MigrationManager(new Migration(Container::get('db'))))->down();
    }


}