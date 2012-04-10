{SessionModel} = require 'models/session_model'
{GenericView} = require 'views/generic_view'

{baseContext, serializeForm} = require 'helpers'

class exports.SignupView extends GenericView
  className: 'signup'
  template: require './templates/signup'
  events:
    "click #signup-form button[type='submit']": "submit"

  initialize: ->
    @model = new SessionModel

    # app.homeView.getCurrentUser
    #   success: (model, resp) =>
    #     @model.set model.toJSON(), silent: true

  render: ->
    @$el.html @template(baseContext)
    @el

  submit: (ev) ->
    $form = $(ev.target).parents 'form'
    @clearErrors()
    formData = serializeForm $form
    @model.save formData,
      success: (model, response) ->
        if !response.is_anonymous
          app.router.navigate "!/profiles/#{response.uid}", trigger: true
      error: (model, response) =>
        if response.responseText?
          for field, message of JSON.parse(response.responseText)
            @renderError field, message
        else
          for field, message of response
            @renderError field, message

    # error event listener
    return false
