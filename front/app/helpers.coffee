class exports.BrunchApplication
  constructor: ->
    $ =>
      @initialize this
      Backbone.history.start()

  initialize: ->
    null


exports.baseContext =
  baseField: (attr, type, placeholder) ->
    @safe "<input type='#{type}' name='#{attr}' id='id_#{attr}' class='input-large' placeholder='#{placeholder}' />"
  formFor: (id, yield) ->
    form =
      textField: (attr, placeholder) =>
        @baseField attr, 'text', placeholder
      passwdField: (attr, placeholder) =>
        @baseField attr, 'password', placeholder
      labelFor: (attr, name) =>
        @safe "<label class='control-label' for='id_#{attr}'>#{name}</label>"
    body = yield form
    @safe "<form class='form-horizontal' id='#{id}'>#{body}</form>"


exports.serializeForm = (form) ->
  [array, response] = [form.serializeArray(), {}]
  for attr in array
    response[attr.name] = attr.value
  response
