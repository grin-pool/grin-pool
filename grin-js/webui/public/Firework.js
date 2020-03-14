/*
    JavaScript Fireworks Animation v.1.0
    Developed by AndesCode (codecanyon.net/user/andescode/portfolio)
*/
"use strict";
var fwSVGns = "http://www.w3.org/2000/svg";
var fwTotal = 0; // Total number of fireworks
var fwActives = {}; // number of active fireworks in the html containers
var explosionSoundCreated = false;
var explosionMP3 = null;

function CFirework(htmlContainerId, fireColor, startX, startY, fwScale)
{
    fwTotal++;
    this.num = fwTotal; // firework identifier

    // Parameters

    this.htmlContainerId = htmlContainerId.toLowerCase(); // ID attribute of the html element that will contain the firework
    this.htmlContainer = document.getElementById(htmlContainerId); // reference to the html element that will contain the firework
    this.fireColor = fireColor; // firework color
    this.startX = startX; // initial x position of the firework
    this.startY = startY; // initial y position of the firework
    // Optional parameter
    this.fwScale = typeof fwScale !== 'undefined' ? fwScale : 1; // scale of the firework

    // Firework elements

    this.SVGcanvas = null; // svg canvas for the html element that contains the animated fireworks
    this.fwContainer = null; // Ascending fireball and explosion container
    this.ascendingFireBall = null;
    this.sparks = null; // tail of the ascending fireball
    this.fastExplosion = null; // fast visual effect at the beginning of the explosion
    this.particles = null;
    this.shineColor = null; // fireworks backlight

    // Attributes

    this.velX = 0; // horizontal velocity
    this.velY = -100; // vertical velocity
    this.gravity = 40;
    this.timeBeforeExplosion = 1500; // in milliseconds
    this.ascendingFireBallRadius = 14; // ascending fireball size
    this.firstExplosionRadius = 45;
    this.numExplosionParticles = 200; // number of particles in the explosion
    this.explosionParticleRadius = 2.5;
    this.explosionVelocity = 180;
    this.explosionDeceleration = 0.96;
    this.explosionParticlesMaxLifespan = 2000; // in milliseconds
    this.shineRadius = 60; // backlight size
    this.shineExpansionTime = 800; // in milliseconds
    this.shineFadeOutTime = 1100; // in milliseconds
    this.useAudio = false;
    this.audioURL = "Explosion.mp3";
    // Not customizable attribute
    this.separation = 118;
    this.fwCenter = 132;
}

// Starts the firework animation
CFirework.prototype.start = function()
{
    // update the number of fireworks in the html container
    if (fwActives.hasOwnProperty(this.htmlContainerId))
    {
        fwActives[this.htmlContainerId] = fwActives[this.htmlContainerId] + 1;
    }
    else {
        fwActives[this.htmlContainerId] = 1;
    }

    this.separation = Math.round(1.6 * (this.shineRadius + this.ascendingFireBallRadius));
    this.fwCenter = this.ascendingFireBallRadius + this.separation;

    // Canvas for the animated SVG elements

    var canvasSVGs = this.htmlContainer.getElementsByClassName("fwSVGcanvas");
    if (canvasSVGs.length > 0) {
        this.SVGcanvas = canvasSVGs[0];
    }
    else {
        this.SVGcanvas = document.createElementNS(fwSVGns, "svg");
        this.SVGcanvas.setAttributeNS(null, "class", "fwSVGcanvas");
        this.SVGcanvas.setAttributeNS(null, "width", this.htmlContainer.offsetWidth);
        this.SVGcanvas.setAttributeNS(null, "height", this.htmlContainer.offsetHeight);
        this.SVGcanvas.setAttributeNS(null, "style", "display:block; position:absolute");
        // Set SVG canvas position
        var fwContainerPosition = getComputedStyle(this.htmlContainer, null).position.toLowerCase();
        if (fwContainerPosition == "absolute" || fwContainerPosition == "fixed" || fwContainerPosition == "relative") {
            this.SVGcanvas.style.top = "0px";
            this.SVGcanvas.style.left = "0px";
        }
        else {
            var offsets = this.htmlContainer.getBoundingClientRect();
            this.SVGcanvas.style.top = offsets.top + "px";
            this.SVGcanvas.style.left = offsets.left + "px";
        }
        this.htmlContainer.appendChild(this.SVGcanvas);
    }

    // SVG containing the firework. Scale of the firework

    this.fwContainer = document.createElementNS(fwSVGns, "svg");
    var xySeparation = (this.separation + this.ascendingFireBallRadius) * this.fwScale;
    this.fwContainer.setAttributeNS(null, "x", this.startX - xySeparation);
    this.fwContainer.setAttributeNS(null, "y", this.startY - xySeparation);
    this.fwContainer.setAttributeNS(null, "width", (this.separation * 2) * this.fwScale);
    this.fwContainer.setAttributeNS(null, "height", (this.separation * 2) * this.fwScale);
    var sizeViewBox = this.separation * 2;
    this.fwContainer.setAttributeNS(null, "viewBox", "0 0 " + sizeViewBox + " " + sizeViewBox);
    this.SVGcanvas.appendChild(this.fwContainer);

    // Prepare explosion audio if required
    if (this.useAudio && !explosionSoundCreated) {
        explosionMP3 = new Audio(this.audioURL);
        explosionSoundCreated = true;
    }

    // GRADIENTS AND FILTERS

    // Gradient for ascending fireball
    this.createGradient(this.fwContainer, "bigFireGrad" + this.num, [
        { offset: "20%", style: "stop-color:#fff;stop-opacity:1" },
        { offset: "45%", style: "stop-color:#" + this.fireColor + ";stop-opacity:0.6" },
        { offset: "100%", style: "stop-color:#" + this.fireColor + ";stop-opacity:0" }
    ]);
    // Glow for sparkles
    this.createFilter(this.fwContainer, "sparklesGlow" + this.num, "FFFFFF", 2);
    // Gradient for explosion
    this.createGradient(this.fwContainer, "explosionGrad" + this.num, [
        { offset: "0%", style: "stop-color:#fff;stop-opacity:1" },
        { offset: "100%", style: "stop-color:#" + this.fireColor + ";stop-opacity:0" }
    ]);
    // Gradient for explosion particles
    this.createFilter(this.fwContainer, "particlesGlow" + this.num, this.fireColor, 4);
    // Explosion background gradient
    this.createGradient(this.fwContainer, "backlightGrad" + this.num, [
        { offset: "20%", style: "stop-color:#" + this.fireColor + ";stop-opacity:0.3" },
        { offset: "100%", style: "stop-color:#" + this.fireColor + ";stop-opacity:0" }
    ]);

    // ANIMATED OBJECTS

    // Ascending fireball
    this.ascendingFireBall = this.createSVG("circle", "bigFire", {
        "cx": this.fwCenter, "cy": this.fwCenter, "r": this.ascendingFireBallRadius,
        "stroke": "none", "fill": "url(#bigFireGrad" + this.num + ")"
    });
    this.fwContainer.appendChild(this.ascendingFireBall);

    // Firework tween
    var removeTime = this.timeBeforeExplosion + Math.max(this.explosionParticlesMaxLifespan, this.shineExpansionTime + this.shineFadeOutTime) + 100;
    var fwTween = this.projectileTween(this.fwContainer, removeTime, deleteFW, this.gravity, this.velX, this.velY);

    var cfw = this;

    // Firework glint

    var exploded = false;
    var arrGlint = [[0.85, 85], [0.6, 30], [0.85, 120], [1, 30]];
    var idx = 0;
    glint();

    function glint()
    {
        if (!exploded) {
            cfw.setSVGscale(cfw.ascendingFireBall, arrGlint[idx][0], cfw.fwCenter, cfw.fwCenter);
            setTimeout(glint, arrGlint[idx][1]);
            idx = idx == (arrGlint.length - 1) ? 0 : idx + 1;
        }
    }

    // sparks tail container
    this.sparks = document.createElementNS(fwSVGns, "svg");
    this.sparks.setAttributeNS(null, "filter", "url(#sparklesGlow" + this.num + ")"); // sparks light effect
    this.sparks.setAttributeNS(null, "x", this.separation);
    this.sparks.setAttributeNS(null, "y", this.separation);
    this.fwContainer.appendChild(this.sparks);
    // Adding a spark every 5 milliseconds:
    var sparksInterval = setInterval(function () { CFirework.prototype.addSpark.call(cfw) }, 5);

    // Delete the ascending fireball. Start the explosion animation

    setTimeout(deleteAscendingFireBall, this.timeBeforeExplosion);

    function deleteAscendingFireBall()
    {
        exploded = true;
        cfw.fwContainer.removeChild(cfw.ascendingFireBall);
        clearInterval(sparksInterval); // stops sparks creation
        // Start explosion
        cfw.explosion();
    }

    // Remove firework
    function deleteFW()
    {
        cfw.fwContainer.removeChild(cfw.particles); // remove particles
        cfw.fwContainer.removeChild(cfw.shineColor);
        cfw.SVGcanvas.removeChild(cfw.fwContainer);

        fwActives[cfw.htmlContainerId] = Math.max(0, fwActives[cfw.htmlContainerId] - 1);
        if (fwActives[cfw.htmlContainerId] == 0) {
            cfw.htmlContainer.removeChild(cfw.SVGcanvas);
        }
    }
}

// Creates SVG element (circle, gradient, filter)
CFirework.prototype.createSVG = function(type, id, attributes)
{
    var SVGfigure = document.createElementNS(fwSVGns, type);
    if (id != null) {
        SVGfigure.setAttributeNS(null, "id", id);
    }
    // set attributes
    for (var key in attributes) {
        SVGfigure.setAttributeNS(null, key, attributes[key]);
    }
    return SVGfigure;
}

// Creates radial gradient
CFirework.prototype.createGradient = function(container, id, stops)
{
    var grad = this.createSVG("radialGradient", id,
        {"cx": "50%", "cy": "50%", "r": "50%", "fx": "50%", "fy": "50%"});
    // Set stop elements
    for (var i = 0; i < stops.length; i++){
        var attrs = stops[i];
        var stop = document.createElementNS(fwSVGns, 'stop');
        // set stop parameters
        for (var attr in attrs) {
            if (!stop.hasAttribute(attr)) {
                stop.setAttribute(attr, attrs[attr]);
            }
        }
        grad.appendChild(stop);
    }
    // insert the gradient inside the 'defs' node
    this.insertDef(container, grad);
}

// Creates a glow effect filter
CFirework.prototype.createFilter = function(container, id, colorHex, stdDeviation)
{
    // get RGB values
    var colorDec = parseInt(colorHex, 16);
    var r = ((colorDec >> 16) & 255) / 255;
    var g = ((colorDec >> 8) & 255) / 255;
    var b = (colorDec & 255) / 255;
    // create svg filter
    var filt = this.createSVG("filter", id, {});
    var cMatrix = this.createSVG("feColorMatrix", null, { "type": "matrix", "values": "0 0 0 " + r + " " + r + "  0 0 0 " + g + " " + g + "  0 0 0 " + b + " " + b + "  0 0 0 1 0" });
    filt.appendChild(cMatrix);
    var gBlur = this.createSVG("feGaussianBlur", null, { "stdDeviation": stdDeviation, "result": "coloredBlur" });
    filt.appendChild(gBlur);
    var fMerge = this.createSVG("feMerge", null, {});
    var fmNode1 = this.createSVG("feMergeNode", null, { "in": "coloredBlur" });
    var fmNode2 = this.createSVG("feMergeNode", null, { "in": "SourceGraphic" });
    fMerge.appendChild(fmNode1);
    fMerge.appendChild(fmNode2);
    filt.appendChild(fMerge);
    // insert the filter inside the 'defs' node
    this.insertDef(container, filt);
}

// inserts an element inside the 'defs' node of the object provided
CFirework.prototype.insertDef = function (container, elem)
{
    var defs = container.querySelector('defs') ||
        container.insertBefore(document.createElementNS(fwSVGns, 'defs'), container.firstChild);
    defs.appendChild(elem);
}

// adds a spark to the tail of the ascending firework
CFirework.prototype.addSpark = function()
{
    var sparkTime = 400 + (Math.random() * 800); // spark's lifespan
    var sparkVelX = this.velX + (Math.random() * 20) - 10; // horizontal velocity
    var sparkVelY = (Math.random() * 80) + 40; // vertical velocity
    // Spark's initial position
    var x = this.ascendingFireBallRadius + (Math.random() * 3) - 1.5;
    var y = this.ascendingFireBallRadius + Math.random() * 4;

    var sparksContainer = this.sparks;
    // Create Spark
    var spark = CFirework.prototype.createCircle.call(this, sparksContainer, x, y, 1, "FFEEB8");
    // Spark's motion
    this.projectileTween(spark, sparkTime, deleteSpark, 0, -sparkVelX, sparkVelY, 1, 0);
    // delete the spark when its motion ends
    function deleteSpark() {
        sparksContainer.removeChild(spark);
    }
}

// Creates the explosion animation
CFirework.prototype.explosion = function()
{
    var cfw = this;
    
    // adding backlight color
    this.shineColor = this.createSVG("circle", "shineColor",
        {"cx": this.fwCenter, "cy": this.fwCenter, "r": this.shineRadius,
            "stroke": "none", "fill": "url(#backlightGrad" + this.num + ")"});
    this.fwContainer.appendChild(this.shineColor);

    // Adding explosion
    this.fastExplosion = this.createSVG("circle", "explosion",
        {"cx": this.fwCenter, "cy": this.fwCenter, "r": this.firstExplosionRadius,
            "stroke": "none", "fill": "url(#explosionGrad" + this.num + ")"});
    this.fwContainer.appendChild(this.fastExplosion);

    // animating fast explosion
    var anim = this.animation(65, animFastExplosion, function() { cfw.fwContainer.removeChild(cfw.fastExplosion); });

    function animFastExplosion(progress)
    {
        if (15 < progress && progress < 40) {
            cfw.setSVGscale(cfw.fastExplosion, 1.67, cfw.fwCenter, cfw.fwCenter);
        }
        if (40 <= progress && progress < 65) {
            cfw.setSVGscale(cfw.fastExplosion, 1, cfw.fwCenter, cfw.fwCenter);
        }
    }

    // Adding explosion particles

    this.particles = document.createElementNS(fwSVGns, "svg");
    this.particles.setAttributeNS(null, "filter", "url(#particlesGlow" + this.num + ")");

    var particlesContainer = this.particles;

    for (var i = 0; i < this.numExplosionParticles; i++)
    {
        var vVel = Math.pow(Math.random(), 0.3) * this.explosionVelocity; // Vector velocity
        var epAngle = Math.random() * 2 * Math.PI; // angle
        var epVelX = vVel * Math.sin(epAngle); // Velocity in X
        var epVelY = vVel * Math.cos(epAngle); // Velocity in Y
        var epTime = 50 + (Math.random() * this.explosionParticlesMaxLifespan); // particle's lifespan
        // Create and add particle
        var explosionParticle = this.createCircle(this.particles, this.fwCenter, this.fwCenter, this.explosionParticleRadius, "FFFFFF", this.fireColor);
        // Particle movement and fading
        var xpTween = this.explosionParticleTween(explosionParticle, epTime,
            this.explosionParticleRadius, this.explosionDeceleration, epVelX, epVelY);
    }
    this.fwContainer.appendChild(this.particles);
    
    // Backlight expansion and fade-out animations

    var animBL = this.animation(this.shineExpansionTime, updateScaleBL, shineFadeOut);

    // expansion function
    function updateScaleBL(progress) {
        var t = Math.min(progress / cfw.shineExpansionTime, 1);
        var newScale = 0.9 + (0.7 * (t * (2 - t)));
        cfw.shineColor.setAttribute("r", newScale * cfw.shineRadius);
    }

    // starts backlight's fade out
    function shineFadeOut() {
        var animFO = cfw.animation(cfw.shineFadeOutTime, updateFadeOut, null);
    }

    function updateFadeOut(progress) {
        var t = Math.min(progress / (cfw.shineFadeOutTime), 1);
        var opacityLevel = 1 - (t * t);
        cfw.shineColor.setAttribute('fill-opacity', opacityLevel);
    }

    // Play explosion sound

    if (this.useAudio) {
        explosionMP3.currentTime = 0
        explosionMP3.play();
    }
}

// creates an svg circle
CFirework.prototype.createCircle = function(target, cx, cy, radius, fillColor, strokeColor)
{
    strokeColor = typeof strokeColor !== 'undefined' ? "#" + strokeColor : "none";
    var fire = document.createElementNS(fwSVGns, "circle");
    fire.setAttributeNS(null, "cx", cx);
    fire.setAttributeNS(null, "cy", cy);
    fire.setAttributeNS(null, "r", radius);
    fire.setAttributeNS(null, "fill", "#" + fillColor);
    fire.setAttributeNS(null, "stroke", strokeColor);
    if (strokeColor != "none") {
        fire.setAttributeNS(null, "stroke-width", 0.5);
    }
    target.appendChild(fire);
    return fire;
}

// Motion for firework and sparkles
CFirework.prototype.projectileTween = function(tweenedObject, timeRequired, endFunc, gravity, velX, velY, startOpacity, endOpacity)
{
    // optional parameters
    startOpacity = typeof startOpacity !== 'undefined' ? startOpacity : 1;
    endOpacity = typeof endOpacity !== 'undefined' ? endOpacity : 1;

    var changeOpacity = (startOpacity != endOpacity); // determines if the opacity must change
    var OpacityInterval = endOpacity - startOpacity; // difference between initial and final opacity level
    var timePassed = 0;
    var lastTime = 0;

    var isFigure = tweenedObject.nodeName != "svg"; // true: tweenedObject is a circle / false: tweenedObject is an svg node

    // set initial opacity
    if (changeOpacity) {
        if (isFigure) {
            tweenedObject.setAttribute('fill-opacity', startOpacity + "");
        }
        else {
            tweenedObject.style.opacity = startOpacity;
        }
    }

    var cfw = this;

    // Projectile motion tween

    var anim = this.animation(timeRequired, updateProjectile, endFunc);

    function updateProjectile(progress)
    {
        timePassed = progress - lastTime;
        lastTime = progress;
        // update vertical velocity
        var adjustment = timePassed / 1000;
        velY += gravity * adjustment;
        // update position
        var attX = isFigure ? "cx" : "x";
        var attY = isFigure ? "cy" : "y";
        cfw.increaseParameter(tweenedObject, attX, velX * adjustment);
        cfw.increaseParameter(tweenedObject, attY, velY * adjustment);
        // update opacity level if required
        if (changeOpacity) {
            var newOpacity = startOpacity + (OpacityInterval * (progress / timeRequired));
            if (isFigure) {
                tweenedObject.setAttribute('fill-opacity', newOpacity);
            }
            else {
                tweenedObject.style.opacity = newOpacity;
            }
        }
    }
}

// Motion for explosion particles
CFirework.prototype.explosionParticleTween = function (tweenedObject, timeRequired, explosionParticleRadius, acceleration, velX, velY)
{
    var cfw = this;
    var timePassed = 0;
    var lastTime = 0;

    var anim = this.animation(timeRequired, updateParticle, null);

    // updates the position and size of the particle
    function updateParticle(progress)
    {
        timePassed = progress - lastTime;
        lastTime = progress;

        // update velocity
        var velIncrease = Math.pow(acceleration, timePassed / 17);
        velX *= velIncrease;
        velY *= velIncrease;
        // update position
        var advance = timePassed / 1000;
        cfw.increaseParameter(tweenedObject, "cx", velX * advance);
        cfw.increaseParameter(tweenedObject, "cy", velY * advance);
        // update scale
        var newScale = 1 - (0.9 * (progress / timeRequired));
        newScale = Math.max(newScale, 0.01);
        tweenedObject.setAttribute("r", newScale * explosionParticleRadius);
        tweenedObject.setAttribute("stroke-width", 0.5 * newScale);
    }
}

// General animation method
CFirework.prototype.animation = function(timeLimit, updateFunc, endFunc)
{
    endFunc = typeof endFunc !== 'undefined' ? endFunc : null;
    var start = null;
    animate(); // start animation

    // function called repeatedly until the time limit is reached
    function animate() {
        // elapsed time
        var ts = new Date().getTime();
        if (start === null)
            start = ts;
        var progress = ts - start;

        // Update the animated object using the provided function
        updateFunc(progress);

        // continue or stop the animation
        if (progress < timeLimit) {
            // invoke again the "animate" function (60 times per second approx.)
            setTimeout(animate, 15);
        }
        else {
            // call the "endFunc" function, if provided, when the time limit is reached
            if (endFunc != null) {
                endFunc();
            }
        }
    }
}

// increases the value of a parameter in a node
CFirework.prototype.increaseParameter = function (obj, param, value)
{
    obj.setAttribute(param, parseFloat(obj.getAttribute(param)) + value);
}

// changes the scale of a svg circle
CFirework.prototype.setSVGscale = function(obj, scale, cx, cy)
{
    obj.setAttribute("transform", "scale(" + scale + ")");
    obj.setAttribute("cx", cx + (((1 - scale) * cx) / scale));
    obj.setAttribute("cy", cy + (((1 - scale) * cy) / scale));
}

// Creates and starts a firework after a given time
function FireworkTimer(ftHtmlContainerId, ftFireColor, ftStartX, ftStartY, ftDelayTime, pftUseSound, pftScale, pftVelX)
{
    var ftUseSound = typeof pftUseSound !== 'undefined' ? pftUseSound : false; // use sound explosion
    var ftScale = typeof pftScale !== 'undefined' ? pftScale : 1; // scale of the firework
    var ftVelX = typeof pftVelX !== 'undefined' ? pftVelX : 0; // horizontal velocity

    // create and start a firework after [ftDelayTime] milliseconds
    setTimeout(function () {
        var fwt = new CFirework(ftHtmlContainerId, ftFireColor, ftStartX, ftStartY, ftScale);
        fwt.useAudio = ftUseSound;
        fwt.velX = ftVelX;
        fwt.start();
    }, ftDelayTime);
}