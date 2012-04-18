{SessionModel} = require 'models/session_model'

class exports.GenericView extends Backbone.View

  baseContext:
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


  serializeForm: (form) ->
    [array, response] = [form.serializeArray(), {}]
    for attr in array
      response[attr.name] = attr.value
    response


  renderError: (field, message) ->
    $el = @$el.find "form input[name='#{field}']"
    $el.parents(".control-group").addClass 'error'
    error = $(document.createElement('span')).addClass('help-inline error').text(message).hide()
    $el.after error
    error.fadeIn()


  clearErrors: ->
    @$el.find(".control-group").removeClass 'error'
    @$el.find("span.help-inline.error").slideUp().remove()


  getCurrentUser: (options) ->
    @session = new SessionModel
    if options?
      @session.fetch
        success: options.success
        error: options.error


  redirectAuthenticated: ->
    @getCurrentUser
      success: (model, resp) ->
        unless model.get('is_anonymous')
          routePath = "!/profiles/#{model.get 'uid'}"
          app.router.navigate routePath, trigger: true


  redirectAnonymous: ->
    @getCurrentUser
      success: (model, resp) ->
        if model.get('is_anonymous')
          app.router.navigate "", trigger: true
