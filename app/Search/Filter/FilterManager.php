<?php


namespace App\Search\Filter;


use App\Database\Filter;

class FilterManager
{


    /**
     * @var array
     */
    private $filters = [];







    /**
     *
     * Get new Instance of Itself.
     *
     * @return static
     */
    public static function make()
    {
        return new static;
    }








    /**
     * Add Filter.
     *
     * @param string $name
     * @param Filter $filter
     * @return $this
     */
    public function add($name, Filter $filter)
    {
        $this->filters[$name] = $filter;

        return $this;
    }







    /**
     * Get Filter by index.
     *
     * @param string $name
     * @return Filter
     */
    public function get($name)
    {
        return $this->filters[$name];
    }






    /**
     * Get All Filters.
     *
     * @return array
     */
    public function all()
    {
        return $this->filters;
    }






    /**
     * Get Keys.
     *
     * @return array
     */
    public function Keys()
    {
        return array_keys($this->filters);
    }


}