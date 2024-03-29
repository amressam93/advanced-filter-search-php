<?php

use Faker\Factory;

trait ModelData
{
    /**
     * @var null|\Faker\Generator
     */
    protected $faker = null;


    /**
     * Get Faker Instance.
     *
     * @return \Faker\Generator|null
     */
    protected function faker()
    {
        if(is_null($this->faker))
        {
            $this->faker = Faker\Factory::create();
        }
        return $this->faker;

    }


    /**
     * Get Book Data
     *
     * @param array $user_data
     */
    protected function bookData(array $user_data = [])
    {
       return $this->mergeData(
       [
           'category_id' => $this->faker()->numberBetween(1,10),
           'isbn'=>$this->faker()->isbn10,
           'year'=>$this->faker()->year,
           'title'=>$this->faker()->words(3,true),
           'description'=>$this->faker()->sentence,
           'price'=>$this->faker()->randomFloat(2)

       ],
       $user_data);
    }


    /**
     * Merge Data.
     *
     * @param array $data
     * @param array $user_data
     * @return array
     */
    protected function mergeData(array $data, array $user_data = [])
    {
        if(! empty($user_data))
        {
            $data = array_merge($data,$user_data);
        }
        return $data;


    }


    /**
     * lookup table data.
     *
     * @param array $user_data
     * @param string $property
     * @return array
     */
    protected function lookupData(array $user_data = [], $property = 'word')
    {
        return $this->mergeData(['name' => $this->faker()->{$property}],$user_data);
    }


}