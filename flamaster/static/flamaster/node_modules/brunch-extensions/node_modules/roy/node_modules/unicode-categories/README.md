# Unicode categories
Unicode categories regExps.

## Installation

```bash
npm install unicode-categories
```

## Usage

```javascript
var unicode = require('unicode-categories');
// Tests if text is a valid unicode upper case letter.
var isValidUpperCase = unicode.Lu.test;
// Tests if text is a valid ecmascript identifier.
var isValidIdentifier = unicode.ECMA.identifier.test;
```

## Documentation
Library contains several unicode category regexps. Here's list of them:

(short name, long name: description)

- `Lu`: upper case letter.
- `Ll`: lower case letter.
- `Lt`: title case letter.
- `Lm`: modifier letter.
- `Lo`: other letter.
- `Mn`: non-spacing mark.
- `Mc`: space mark.
- `Nl`: number letter.
- `Nd`: decimal (e.g. 0-9 etc).
- `Pc`: punctuation connector.

Also, unicode-categories gives you a list of ECMAscript idenfitiers:

- `ECMA.start` - letter, that identifier starts with. Contains letters from
categories (Lu, Ll, Lt, Lm, Lo, Nl). Also it can be `$` and `_`.
- `ECMA.part` - all `ECMA.start` letters plus letters from categories Mn, Mc, Nd, Pc.
- `ECMA.idenfitier` - combination of previous two regexps.

For details, see [ECMAscript spec](http://es5.github.com/#x7.6).

## License
(The MIT License)

Copyright (c) 2011 Paul Miller (http://paulmillr.com/)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

