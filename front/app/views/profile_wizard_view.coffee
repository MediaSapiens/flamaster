{GenericView} = require 'views/generic_view'
{ProfileModel} = require 'models/profile_model'

class exports.ProfileWizardView extends GenericView
  className: 'profile-wizard'
  template: require './templates/profile_wizard'

  events:
    "click #profile-wizard button": "submit"
    "submit #profile-wizard": "submit"

  push: (options) ->
    mediator.trigger options.action, {token: options.token}

  render: (options) ->
    @model = new ProfileModel options.model
    @model.save options.model,
      success: (args...) -> console.log 'success', args
      error: (model, xhr, options) -> console.log 'error'
    @$el.html @template(@baseContext)
    return @el

  submit: (ev) ->
    @clearErrors()
    data = @serializeForm @$el.find("#profile-wizard")
    @model.save data,
      success: (args...) -> console.log 'success', args
      error: (model, response) =>
        if response.responseText?
          try
            parsedResponse = JSON.parse response.responseText
            for field, message of parsedResponse
              @renderError field, message
          catch error
            console.warn error
        else
          for field, message of response
            @renderError field, message
        false
    false
