{SessionModel} = require 'models/session_model'
{GenericView} = require 'views/generic_view'

{baseContext, serializeForm} = require 'helpers'

class exports.SignupView extends GenericView
      template: require './templates/signup'
      className: 'signup'

      events:
        "click #signup-form button[type='submit']": "submit"
        # "submit #signup-form": "submit"


      initialize: ->
        @$el.find("#signup-form").submit ->
          console.log arguments
          return false

      render: ->
        @$el.html @template(baseContext)
        @el

      submit: (ev) ->
        $form = $(ev.target).parents 'form'
        @clearErrors()
        formData = serializeForm $form
        session = new SessionModel formData
        session.on 'error', (session, error) =>
          for field, message of error
            @renderError field, message
        session.save
          success: ->
            console.log arguments
          error: ->
            console.log arguments
        # error event listener
        return false
