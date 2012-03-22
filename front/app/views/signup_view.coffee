{SessionModel} = require 'models/session_model'
{baseContext, serializeForm} = require 'helpers'

class exports.SignupView extends Backbone.View
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

      renderError: (field, message) ->
        $el = @$el.find "form input[name='#{field}']"
        $el.parents(".control-group").addClass 'error'
        error = $(document.createElement('span')).addClass('help-inline error').text message
        $el.after error

      clearErrors: ->
        @$el.find(".control-group").removeClass 'error'
        @$el.find("span.help-inline.error").remove()

