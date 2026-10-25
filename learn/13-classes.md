# 13. Classes

[Learn Pin](README.md) · previous: [12. Modules and packages](12-modules-and-packages.md) · next: [14. Tasks and real time](14-tasks-and-realtime.md)

A class groups related values (its **properties**) together with the functions that work on them (its
**methods**). Pin writes classes the way PHP 8 does. The difference: an object is a **value with one owner**,
just like a list (chapter 7). Pin has no inheritance.

## A first class

```php
class Product {
    public string $name;
    public int $price;
    public int $stock = 0;            // a default value

    function __construct(string $name, int $price) {
        $this->name = $name;
        $this->price = $price;
    }

    function inStock(): bool {
        return $this->stock > 0;
    }

    function restock(int $n): void {
        $this->stock += $n;
    }
}

$tea = new Product("tea", 40);
echo $tea->name, " ", $tea->inStock() ? "in stock" : "sold out", "\n";
$tea->restock(5);
echo "{$tea->name}: {$tea->stock} left\n";
echo json_encode($tea), "\n";
```

Output:

```text
tea sold out
tea: 5 left
{"name":"tea","price":40,"stock":5}
```

- `new Product(...)` runs `__construct`. When the constructor ends, every property must have a value: either
  a default (`= 0`) or one the constructor set on every path. The compiler checks this.
- A default must be a literal, such as `0`, `"text"`, `false`, `[]` or `[1, 2]`.
- `json_encode` writes the public properties, in the order they are declared.

A constructor that only copies its parameters into properties can **promote** them (PHP 8 syntax):

```php
class Point {
    public function __construct(public int $x, public int $y) {}

    function moved(int $dx): Point {
        return new Point($this->x + $dx, $this->y);
    }
}

$p = new Point(1, 2);
echo json_encode($p->moved(10)), "\n";
```

Output:

```text
{"x":11,"y":2}
```

## public and private

A `private` property or method can be used only inside the class's own methods. `json_encode` leaves private
properties out.

<!-- check: error -->
```php
class Account {
    private int $pin = 1234;
    public function __construct(public string $owner) {}
}

$a = new Account("Ann");
echo json_encode($a), "\n";
echo $a->pin;
```

Error:

```text
example.pn:8: error: Account::$pin is private: only the methods of Account can use it
```

## Objects in lists, maps and other objects

Types nest freely: `list<Product>`, `map<string,Product>`, a `list<string>` inside an object, a
`list<list<int>>`. You can change a value deep inside such a structure through its **path**:

```php
class Item {
    public function __construct(public string $name, public int $price) {}
}

class Order {
    public list<Item> $items = [];
    public list<string> $notes = [];

    function total(): int {
        $t = 0;
        foreach ($this->items as $it) { $t += $it->price; }
        return $t;
    }
}

$o = new Order();
$o->items[] = new Item("tea", 40);
$o->items[] = new Item("cake", 120);
$o->items[1]->price -= 20;            // change through a path
$o->notes[] = "no sugar";
echo $o->total(), "\n";
echo json_encode($o), "\n";
```

Output:

```text
140
{"items":[{"name":"tea","price":40},{"name":"cake","price":100}],"notes":["no sugar"]}
```

Classes are also the way to build a JSON object whose values have different types, which a `map` cannot
hold.

## One owner: move, copy, lend

Objects follow the ownership rules of chapter 7:

- `$b = $a;` **moves** the object, so `$a` cannot be used after it.
- `copy($a)` makes a separate object, including everything inside it.
- A parameter `Order $o` is a **read-only loan**.

<!-- check: error -->
```php
class Box { public int $n = 0; }

$a = new Box();
$b = $a;
echo $a->n;
```

Error:

```text
example.pn:5: error: $a was moved on line 4 and can no longer be used here. Use copy($a) if you need two separate values
```

To let a function change the caller's object, mark the parameter with `&`, and write `&` at the call as well.
Then anyone reading the call can see that the function may change the object:

```php
class Order {
    public function __construct(public int $total) {}
}

function discount(Order &$o, int $pct): void {
    $o->total = intdiv($o->total * (100 - $pct), 100);
}

$order = new Order(200);
discount(&$order, 10);
echo $order->total, "\n";
```

Output:

```text
180
```

`&` works for any type, for example `function addTax(int &$satang)`, and for paths such as `&$orders[0]`.

## Methods that change the object

A method that assigns to `$this->...`, or calls another method that does, is a **changing method**. You do
not mark it; the compiler works it out. You can call a changing method only on something you are allowed to
change, so calling one on a read-only parameter fails:

<!-- check: error -->
```php
class Counter {
    public int $n = 0;
    function inc(): void { $this->n += 1; }
}

function bump(Counter $c): void {
    $c->inc();
}
```

Error:

```text
example.pn:7: error: $c is a parameter lent to this function read-only, so it cannot be changed by inc(). To change the caller's value declare it as Counter &$c (and call with &$value); or work on $copy = copy($c);
```

To change every item of a list in a loop, use `foreach` with `&`:

```php
class Counter {
    public int $n = 0;
    function inc(): void { $this->n += 1; }
}

$cs = [new Counter(), new Counter()];
foreach ($cs as &$c) { $c->inc(); $c->inc(); }
echo json_encode($cs), "\n";
```

Output:

```text
[{"n":2},{"n":2}]
```

## Borrowing without copying

`$u = $users[0];` does not copy the object. `$u` **borrows** it read-only. While `$u` is still used later in
the function, `$users` cannot change, because the change could free the object `$u` is looking at:

<!-- check: error -->
```php
class User {
    public function __construct(public string $name) {}
}

$users = [new User("ann")];
$u = $users[0];
$users[] = new User("bob");
echo $u->name;
```

Error:

```text
example.pn:7: error: cannot change $users here: $u borrows from it and is used again on line 8. Use $u for the last time before this line, or keep your own value with $u = copy(...)
```

To fix it, use `$u` before you change `$users`, or take your own copy with `$u = copy($users[0]);`.

## Not in Pin

These PHP features are not in Pin:

- `extends`, `abstract`, interfaces, traits, `static`, `protected`.
- `null` and `?->`: every property always has a value.
- Default values for parameters.
- `==` between objects: compare their properties instead.
- A class that holds itself directly: use `list<Node>` or store an id.

## Try it

Write a class `Cart` with a `map<string,int>` of quantities. Give it a method `add(string $item)` that adds
one to the item's quantity and a method `count(): int` that returns the total number of items. Then print
`json_encode($cart)` after adding `"tea"` twice and `"cake"` once.

<details><summary>One answer</summary>

```php
class Cart {
    public map<string,int> $qty = [];

    function add(string $item): void { $this->qty[$item] += 1; }

    function count(): int {
        $n = 0;
        foreach ($this->qty as $q) { $n += $q; }
        return $n;
    }
}

$cart = new Cart();
$cart->add("tea");
$cart->add("tea");
$cart->add("cake");
echo $cart->count(), " ", json_encode($cart), "\n";
```

Output:

```text
3 {"qty":{"tea":2,"cake":1}}
```

</details>
