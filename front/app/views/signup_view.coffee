{SessionModel} = require 'models/session_model'
{GenericView} = require 'views/generic_view'

{baseContext, serializeForm} = require 'helpers'

class exports.SignupView extends GenericView
  className: 'signup'
  events:
    "click #signup-form button[type='submit']": "submit"
  templates:
    'signup:start': require './templates/signup'
    'signup:complete': require './templates/signup_complete'

  render: (options) ->
    console.log options
    @$el.html(options.model.template baseContext)
    @el

  push: (options) ->
    mediator.trigger options.action, template: @templates[options.action]

  submit: (ev) ->
    model = new SessionModel
    $form = $(ev.target).parents 'form'
    @clearErrors()
    formData = serializeForm $form
    model.save formData,
      success: (model, response) ->
        response.uid? and app.router.navigate "!/signup/complete", trigger: true
      error: (model, response) =>
        if response.responseText?
          for field, message of JSON.parse(response.responseText)
            @renderError field, message
        else
          for field, message of response
            @renderError field, message

    # error event listener
    return false
