<?php


namespace App\Search;


class Sticky
{

    /**
     * @var Search
     */
    private $search;


    /**
     * Sticky constructor.
     * @param Search $search
     */
    public function __construct(Search $search)
    {
        $this->search = $search;
    }


    /**
     * sticky text field.
     *
     * @param string $name
     * @param null|mixed $default
     * @return mixed
     */
    public function text($name, $default = null)
    {
        if(! $this->search->has($name))
        {
            return $default;
        }

        return $this->search->get($name);

    }


    /**
     * Sticky select.
     *
     * @param string $name
     * @param mixed $value
     * @param mixed $default
     * @return string|null
     */
    public function select($name, $value, $default = null)
    {
        if(! $this->search->has($name))
        {
            return $this->selectDefault($value,$default);

        }

        if($this->search->get($name) != $value)
        {
            return null;
        }

        return $this->selected();

    }


    /**
     * Sticky default select.
     *
     * @param mixed $value
     * @param mixed $default
     * @return string|null
     */
    private function selectDefault($value, $default = null)
    {
        if(is_null($default) || $value != $default)
        {
            return null;
        }

        return $this->selected();

    }


    /**
     * Selected Attribute.
     *
     * @return string
     */
    private function selected()
    {
        return ' selected="selected"';
    }


    /**
     * sticky radio button.
     *
     * @param string $name
     * @param mixed $value
     * @param mixed $default
     * @return string|null
     */
    public function radio($name, $value, $default = null)
    {
        if(! $this->search->has($name))
        {
            return $this->radioDefault($value,$default);
        }

        if($this->search->get($name) != $value)
        {
            return null;
        }

        return $this->checked();

    }


    /**
     * sticky default checked.
     *
     * @param mixed $value
     * @param mixed $default
     * @return string|null
     */
    private function radioDefault($value, $default = null)
    {
        if(is_null($default) || $value != $default)
        {
            return null;
        }
        return $this->checked();

    }


    /**
     * checked attribute.
     *
     * @return string
     */
    private function checked()
    {
        return ' checked="checked"';
    }


    /**
     * sticky checkbox (single).
     *
     * @param string $name
     * @param mixed $value
     * @param false $checked
     * @return string|null
     */
    public function checkbox($name, $value, $checked = false)
    {
        if(! $this->search->has($name))
        {
            return $this->checkTrue($checked);
        }

        if($this->search->get($name) != $value)
        {
            return null;
        }

        return $this->checked();
    }


    /**
     * Default sticky checkbox (single).
     *
     * @param bool $checked
     * @return string|null
     */
    private function checkTrue($checked = false)
    {
        if(! $checked)
        {
            return null;
        }

        return $this->checked();
    }


    /**
     * sticky checkbox (array).
     *
     * @param string $name
     * @param mixed $value
     * @param array $checked
     * @return string|null
     */
    public function checkboxArray($name, $value, array $checked = [])
    {
        if($this->search->has($name))
        {
            $checked = $this->search->get($name);
        }

        return $this->checkedInArray($value,$checked);

    }


    /**
     * Default sticky checkbox (array).
     *
     * @param mixed $value
     * @param array $checked
     * @return string|null
     */
    private function checkedInArray($value, array $checked = [])
    {
        if(! in_array($value,$checked))
        {
            return null;
        }

        return $this->checked();

    }


}