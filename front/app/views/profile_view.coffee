{SessionModel} = require 'models/session_model'
{ProfileModel} = require 'models/profile_model'

{GenericView} = require 'views/generic_view'

{baseContext, serializeForm} = require 'helpers'

class exports.ProfileView extends GenericView
  className: 'profile'
  template: require './templates/profile'

  events:
    "click a#edit-profile": "editProfile"

  actions: ->
    show: =>
      baseContext = _.extend baseContext,
        profile: @model
      @$el.html @template(baseContext)
      @el

  initialize: (options) ->
    console.log 'profile view:', options
    @session = new SessionModel
    @model = new ProfileModel id: options.id

    app.homeView.getCurrentUser
      success: (model, resp) =>
        @session.set model.toJSON(), silent: true
        @model.fetch
          success: =>
            @render()

  render: (action) ->
    @actions[action]()


  editProfile: (args...) ->
    console args
