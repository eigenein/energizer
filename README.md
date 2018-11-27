# IFFTTie

This is yet another home automation service.

## Why not [Home Assistant](https://www.home-assistant.io/) or [OpenHAB](https://www.openhab.org/)?

There're multiple reasons why I didn't like them:

- Quite heavy. Their restart or configuration update takes ages.
- I can't catch all those _things_, _entities_, _channels_ and etc and relations between them. I want something simpler.
- Too flexible. While this may be good, I'm getting tired configuring all those _things_.
- Custom automation syntax. This may be perfect for non-developers, but I prefer to write in [my favorite language](https://www.python.org/).
- Inconvenient configuration. It's stored inside a container, separate web interfaces are needed to edit it via browser.

## General Idea

In IFFTTie there're only **two** terms to understand: *service* and *update*.

### What's a *service*?

*Service* is an interface to the outside world. It serves two goals:

- You control the outside world with its public methods.
- It generates *updates*.

#### Examples

- [Nest API](https://developers.nest.com/documentation/api-reference)
- [Buienradar](https://www.buienradar.nl/)
- [IFFTT](https://ifttt.com/maker_webhooks)

### What's *update*?

The term stands for itself. Update contains information that something has changed in the world. An update consists of a *key* and a *value*. *Key* is a globally unique identifier which is used to refer to a particular *value* in the world.

#### Examples

| key                                  | value     |
| ------------------------------------ | --------- |
| `buienradar:6391:temperature`        | `2.8`     |
| `nest:camera:0123…9876:is_streaming` | `true`    |
| `webhook:hello`                      | `'world'` |

## Configuration

IFTTTie reads its configuration from a single file. And there're two important things:

- It's **non-local**. You pass a **URL** via command line parameter or environment variable. IFTTTie loads the file when (re-)started. Think here of a secret [Gist](https://gist.github.com/) URL, for example. **Never share your configuration publicly as soon as it contains any credentials.**
- It's a **Python module**. You can write any valid Python code in there. **Don't blindly trust others code.**

## Startup

IFTTTie imports the configuration module at its (re-)start. There're some special globals that you want to define:

### `http_port: int`

Yeah, that's just HTTP port to listen to.

### `async def handle(event: Event)`

This is a function that will be called for every generated event. You can use apply logic in there, of course.

## `class Event`

### `key: str`

This just an event key that I described above.

### `value: Any`

The related value. Very specific to a particular service.

## Service classes

### `Nest`

TODO

### `IFTTT`

TODO

### `Buienradar`

TODO
