{SessionModel} = require 'models/session_model'

class exports.GenericView extends Backbone.View

  renderError: (field, message) ->
    $el = @$el.find "form input[name='#{field}']"
    $el.parents(".control-group").addClass 'error'
    error = $(document.createElement('span')).addClass('help-inline error').text message
    $el.after error

  clearErrors: ->
    @$el.find(".control-group").removeClass 'error'
    @$el.find("span.help-inline.error").remove()

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
