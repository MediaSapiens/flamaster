{SessionModel} = require 'models/session_model'

class exports.SignupView extends Backbone.View
      template: require './templates/signup'

      events:
        "click #signup-form button[type='submit']": "submit"
        # "submit #signup-form": "submit"


      initialize: ->
        @$el.find("#signup-form").submit ->
          console.log arguments
          return false

      serializeForm: (form) ->
        [array, response] = [form.serializeArray(), {}]
        for attr in array
          response[attr.name] = attr.value
        response

      render: ->
        @$el.html @template()
        @el

      submit: (ev) ->
        $form = $(ev.target).parents 'form'
        @clearErrors()
        formData = this.serializeForm $form
        session = new SessionModel formData
        session.on 'error', (session, error) =>
          for field, message of error
            @renderError field, message
        session.save()
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

