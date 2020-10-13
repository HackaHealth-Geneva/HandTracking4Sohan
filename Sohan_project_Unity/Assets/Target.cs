using System.Collections;
using System.Collections.Generic;
using UnityEngine;
//Timer
using System.Diagnostics;
using System;

public class Target : MonoBehaviour
{

     public int thresholdmillisSelection= 3000; 

    //timer 
    Stopwatch stopWatch;

    

    public enum State { Entered, Selected, Commited, Unselected };

    public State currentState; 

    // Start is called before the first frame update
    void Start()
    {
        stopWatch = new Stopwatch();
        TargetUnselected();
        
    }

    // Update is called once per frame
    void Update()
    {
        //UnityEngine.Debug.Log("State: " + currentState); 
    }


    //Cursor inside Target
    public void Inside()
    {
        //UnityEngine.Debug.Log("Inside");

        switch (currentState)
        {
            case State.Entered:
                TargetSelected();
                break;
            case State.Commited:
                TargetCommited();
                break;
            case State.Selected:
                TargetSelected();
                break;
            case State.Unselected:
                TargetEntered();
                break; 
         }
    }

    //cursor outside target
    public void Outside()
    {
        UnityEngine.Debug.Log("Outside");
        TargetUnselected(); 
    }



    public void TargetEntered()
    {
        stopWatch.Start();
        currentState = State.Entered; 
    }


    public void TargetSelected()
    {
         currentState = State.Selected;

        // Get the elapsed time as a TimeSpan value.
        TimeSpan ts = stopWatch.Elapsed;

        if (ts.TotalMilliseconds > thresholdmillisSelection)
        {
            TargetCommited(); 
        }

    }

    public void TargetCommited()
    {
        currentState = State.Commited;
        stopWatch.Stop();
       // Material mate = gameObject.GetComponent<Renderer>().material;
       // mate.color = new Color(0.5f, 1, 1); //C#


    }

    public void TargetUnselected()
    {
        stopWatch.Stop();
        currentState = State.Unselected;
        //Material mate = gameObject.GetComponent<Renderer>().material;
        //mate.color = new Color(0, 0, 0); //C#
    }





}
