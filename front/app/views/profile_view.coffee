{SessionModel} = require 'models/session_model'
{ProfileModel} = require 'models/profile_model'

{GenericView} = require 'views/generic_view'

{baseContext, serializeForm} = require 'helpers'

class exports.ProfileView extends GenericView
  className: 'profile'
  template: require './templates/profile'

  events:
    "click a#edit-profile": "editProfile"

  initialize: (options) ->
    @session = new SessionModel
    @model = new ProfileModel id: options.id

    app.homeView.getCurrentUser
      success: (model, resp) =>
        @session.set model.toJSON(), silent: true
        @model.fetch
          success: =>
            @render()

  render: ->
    baseContext = _.extend baseContext,
      profile: @model
    console.log @model.get 'email'
    @$el.html @template(baseContext)
    @el

  editProfile: (args...) ->
    console args
