class exports.BrunchApplication
  constructor: ->
    $ =>
      @initialize this
      Backbone.history.start()

  initialize: ->
    null


exports.baseContext =
  baseField: (options) ->
    {name, type, placeholder, value} = options
    @safe "<input type='#{type}' name='#{name}' value='#{value or ''}' id='id_#{name}' class='input-large' placeholder='#{placeholder}' />"
  formFor: (id, yield) ->
    form =
      textField: (options) =>
        options.type = 'text'
        @baseField options
      passwdField: (options) =>
        options.type = 'password'
        @baseField options
      labelFor: (options) =>
        {name, text} = options
        @safe "<label class='control-label' for='id_#{name}'>#{text}</label>"
    body = yield form
    @safe "<form class='form-horizontal' id='#{id}'>#{body}</form>"


exports.serializeForm = (form) ->
  [array, response] = [form.serializeArray(), {}]
  for attr in array
    response[attr.name] = attr.value
  response
