<?php


namespace App\Model;


use Error;

abstract class LookupModel extends Model
{


    /**
     * @var int
     */
    public $id;


    /**
     * @var string
     */
    public $name;




    /**
     * Get all records.
     *
     * @return array
     *
     */
    protected function allRecords()
    {
        return $this->orderBy('name')->all();
    }


    /**
     * call all records methods dynamiclly.
     *
     * @param string $name
     * @param array $arguments
     * @return array
     * @throws Error
     */
    public function __call(string $name, array $arguments)
    {
        if($name !== $this->table)
        {
            throw new Error;
        }

        return $this->allRecords();

    }



}