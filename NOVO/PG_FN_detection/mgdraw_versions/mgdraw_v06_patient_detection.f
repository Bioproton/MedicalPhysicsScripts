*$ CREATE MGDRAW.FOR
*COPY MGDRAW
*                                                                      *
*=== mgdraw ===========================================================*
*                                                                      *
      SUBROUTINE MGDRAW ( ICODE, MREG )

      INCLUDE '(DBLPRC)'
      INCLUDE '(DIMPAR)'
      INCLUDE '(IOUNIT)'
*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 1990-2013      by        Alfredo Ferrari           *
*     All Rights Reserved.                                             *
*                                                                      *
*                                                                      *
*     MaGnetic field trajectory DRAWing: actually this entry manages   *
*                                        all trajectory dumping for    *
*                                        drawing                       *
*                                                                      *
*     Created on   01 March 1990   by        Alfredo Ferrari           *
*                                              INFN - Milan            *
*     Last change   12-Nov-13      by        Alfredo Ferrari           *
*                                              INFN - Milan            *
*                                                                      *
*----------------------------------------------------------------------*
*
      INCLUDE '(CASLIM)'
      INCLUDE '(COMPUT)'
      INCLUDE '(SOURCM)'
      INCLUDE '(FHEAVY)'
      INCLUDE '(FLKSTK)'
      INCLUDE '(GENSTK)'
      INCLUDE '(MGDDCM)'
      INCLUDE '(PAPROP)'
      INCLUDE '(QUEMGD)'
      INCLUDE '(SUMCOU)'
      INCLUDE '(TRACKR)'
      INCLUDE '(RESNUC)' 
      INCLUDE '(EVTFLG)'

* RESNUC added by Anna

      DIMENSION DTQUEN ( MXTRCK, MAXQMG )
*
      CHARACTER*20 FILNAM
      LOGICAL LFCOPE
      SAVE LFCOPE
      DATA LFCOPE / .FALSE. /
*
*----------------------------------------------------------------------*
*                                                                      *
*     Icode = 1: call from Kaskad                                      *
*     Icode = 2: call from Emfsco                                      *
*     Icode = 3: call from Kasneu                                      *
*     Icode = 4: call from Kashea                                      *
*     Icode = 5: call from Kasoph                                      *
*                                                                      *
*----------------------------------------------------------------------*
*                                                                      *
      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )
      END IF
*  +-------------------------------------------------------------------*
*  |  Quenching is activated
      IF ( LQEMGD ) THEN
         IF ( MTRACK .GT. 0 ) THEN
            RULLL  = ZERZER
            CALL QUENMG ( ICODE, MREG, RULLL, DTQUEN )
*            WRITE (IODRAW) ( ( SNGL (DTQUEN (I,JBK)), I = 1, MTRACK ),
*     &                         JBK = 1, NQEMGD )
         END IF
      END IF
*  |  End of quenching
*     +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     Boundary-(X)crossing DRAWing:                                    *
*                                                                      *
*     Icode = 1x: call from Kaskad                                     *
*             19: boundary crossing                                    *
*     Icode = 2x: call from Emfsco                                     *
*             29: boundary crossing                                    *
*     Icode = 3x: call from Kasneu                                     *
*             39: boundary crossing                                    *
*     Icode = 4x: call from Kashea                                     *
*             49: boundary crossing                                    *
*     Icode = 5x: call from Kasoph                                     *
*             59: boundary crossing                                    *
*                                                                      *
*======================================================================*

****************END OF CODE BY ANNA****************************

      ENTRY BXDRAW ( ICODE, MREG, NEWREG, XSCO, YSCO, ZSCO )

      RETURN
*======================================================================*
*                                                                      *
*     Event End DRAWing:                                               *
*                                                                      *
*======================================================================*
*                                                                      *
      ENTRY EEDRAW ( ICODE )
      RETURN
*
*======================================================================*
*                                                                      *
*     ENergy deposition DRAWing:                                       *
*                                                                      *
*     Icode = 1x: call from Kaskad                                     *
*             10: elastic interaction recoil                           *
*             11: inelastic interaction recoil                         *
*             12: stopping particle                                    *
*             13: pseudo-neutron deposition                            *
*             14: escape                                               *
*             15: time kill                                            *
*     Icode = 2x: call from Emfsco                                     *
*             20: local energy deposition (i.e. photoelectric)         *
*             21: below threshold, iarg=1                              *
*             22: below threshold, iarg=2                              *
*             23: escape                                               *
*             24: time kill                                            *
*     Icode = 3x: call from Kasneu                                     *
*             30: target recoil                                        *
*             31: below threshold                                      *
*             32: escape                                               *
*             33: time kill                                            *
*     Icode = 4x: call from Kashea                                     *
*             40: escape                                               *
*             41: time kill                                            *
*             42: delta ray stack overflow                             *
*     Icode = 5x: call from Kasoph                                     *
*             50: optical photon absorption                            *
*             51: escape                                               *
*             52: time kill                                            *
*                                                                      *
*======================================================================*
*                                                                      *
      ENTRY ENDRAW ( ICODE, MREG, RULL, XSCO, YSCO, ZSCO )

      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )
      END IF
*      WRITE (IODRAW)  0, ICODE, JTRACK, SNGL (ETRACK), SNGL (WTRACK)
*      WRITE (IODRAW)  SNGL (XSCO), SNGL (YSCO), SNGL (ZSCO), SNGL (RULL)
*  +-------------------------------------------------------------------*
*  |  Quenching is activated : calculate quenching factor
*  |  and store quenched energy in DTQUEN(1, jbk)
      IF ( LQEMGD ) THEN
         RULLL = RULL
         CALL QUENMG ( ICODE, MREG, RULLL, DTQUEN )
*         WRITE (IODRAW) ( SNGL (DTQUEN(1, JBK)), JBK = 1, NQEMGD )
      END IF
*  |  end quenching
*  +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     SOurce particle DRAWing:                                         *
*                                                                      *
*======================================================================*
*
      ENTRY SODRAW
      IF ( .NOT. LFCOPE ) THEN

      END IF
*      WRITE (IODRAW) -NCASE, NPFLKA, NSTMAX, SNGL (TKESUM),
*     &                SNGL (WEIPRI)
*  +-------------------------------------------------------------------*
*  |  (Radioactive) isotope: it works only for 1 source particle on
*  |  the stack for the time being
      IF ( ILOFLK (NPFLKA) .GE. 100000 .AND. LRADDC (NPFLKA) ) THEN
         IARES  = MOD ( ILOFLK (NPFLKA), 100000  )  / 100
         IZRES  = MOD ( ILOFLK (NPFLKA), 10000000 ) / 100000
         IISRES = ILOFLK (NPFLKA) / 10000000
         IONID  = ILOFLK (NPFLKA)
*         WRITE (IODRAW) ( IONID,SNGL(-TKEFLK(I)),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
*  |
*  +-------------------------------------------------------------------*
*  |  Patch for heavy ions: it works only for 1 source particle on
*  |  the stack for the time being
      ELSE IF ( ABS (ILOFLK (NPFLKA)) .GE. 10000 ) THEN
         IONID = ILOFLK (NPFLKA)
         CALL DCDION ( IONID )
*  |
*  +-------------------------------------------------------------------*
*  |  Patch for heavy ions: ???
      ELSE IF ( ILOFLK (NPFLKA) .LT. -6 ) THEN
*         WRITE (IODRAW) ( IONID,SNGL(TKEFLK(I)+AMNHEA(-ILOFLK(NPFLKA))),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
*  |
*  +-------------------------------------------------------------------*
*  |
      ELSE
*         WRITE (IODRAW) ( ILOFLK(I), SNGL (TKEFLK(I)+AM(ILOFLK(I))),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
      END IF
*  |
*  +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     USer dependent DRAWing:                                          *
*                                                                      *
*     Icode = 10x: call from Kaskad                                    *
*             100: elastic   interaction secondaries                   *
*             101: inelastic interaction secondaries                   *
*             102: particle decay  secondaries                         *
*             103: delta ray  generation secondaries                   *
*             104: pair production secondaries                         *
*             105: bremsstrahlung  secondaries                         *
*             110: decay products                                      *
*     Icode = 20x: call from Emfsco                                    *
*             208: bremsstrahlung secondaries                          *
*             210: Moller secondaries                                  *
*             212: Bhabha secondaries                                  *
*             214: in-flight annihilation secondaries                  *
*             215: annihilation at rest   secondaries                  *
*             217: pair production        secondaries                  *
*             219: Compton scattering     secondaries                  *
*             221: photoelectric          secondaries                  *
*             225: Rayleigh scattering    secondaries                  *
*             237: mu pair     production secondaries                  *
*     Icode = 30x: call from Kasneu                                    *
*             300: interaction secondaries                             *
*     Icode = 40x: call from Kashea                                    *
*             400: delta ray  generation secondaries                   *
*  For all interactions secondaries are put on GENSTK common (kp=1,np) *
*  but for KASHEA delta ray generation where only the secondary elec-  *
*  tron is present and stacked on FLKSTK common for kp=npflka          *
*                                                                      *
*======================================================================*
      ENTRY USDRAW ( ICODE, MREG, XSCO, YSCO, ZSCO )

* ****Parameter definitions****                                        *
*                                                                      *
* ICODE = interaction code. Important icodes are 101 for inelastic     *
* interaction, 100 for elastic interaction, 106 for de-excitation, 300 *
* for low energy neutron interaction                                   *
*
* NCASE = history number. For number of primaries = 1000, NCASE will   *
* range from 1 to 1000                                                 *
*
* MREG = current region. Regions values in current NOVO detector model:*
*   1 - 48: Scintillator bars                                          *
*       49: Blackbody                                                  *
*       50: Void outside the detector                                  *
*       51: Void amongst the scintillator bars                         *
*  52 - 55: Void amongst the electronic boxes                          *
*       56: Water phantom phantom                                      *
* 57 - 152: Electric boxes at the ends of each bars                    *
* 153- 200: Air cavities inside the electronic boxes                   *
* 201-xxxx: Target (CT voxels, think big Rubik's cube)                 *
*
* JTRACK = id of the current particle being tracked. If jtrack = 1 it  *
* means that the particle that is being tracked is a proton.           *
* The combination JTRACK.EQ.1 and ICODE.EQ.101 means the current       *       
* interaction was inelastic and caused by a proton.    
*
* NP = Number of secondaries. This is specific to the FLUKA stack 
* called GENSTK, which is the stack where secondary particles are being*
* saved. However, information about the residual nucleus is not saved  * 
* in this stack, but in the FLUKA stack named FHEAVY. If one wishes to *
* loop over FHEAVY, one should use NPHEAV instead of NP. See FHEAVY and* 
* GENSTK files for further information.                                *

* Tki(IP) = kinetic energy of the IPth secondary.                      *
* XSCO,YSCO,ZSCO = X,Y,Z coordinate of the interaction                 * 
* Cxr(IP),Cyr(IP),Czr(IP) = x,y,z cosines of the angle the IPth        * 
* particle was emitted with.                                           *

***** START ADDED BY SANDER IN USDRAW*****************************
*
*-----------------------INTERACTIONS IN TARGET-------------------------------
*
*     If the current region is the target (region 201+)
      IF(MREG .GE. 201) THEN

*       Default flag of true FN/PG is 0 (False)
        LLOUSE = 0

*       Interaction(=source) coordinates
        SPAUSR(2) = XSCO
        SPAUSR(3) = YSCO
        SPAUSR(4) = ZSCO

*       If current interaction code is 101/106 (PG) or 101 (FN)
        IF(ICODE .EQ. 101 .OR. ICODE .EQ. 106) THEN
*
*        If the incoming particle is a proton (1) or generic heavy ion (-2)
         IF(JTRACK .EQ. 1 .OR. JTRACK .EQ. -2) THEN

*         Looping over all the secondaries created in the interaction.
*         If the number of secondaries are 3, then IP ranges from 1 to 3. 
          DO IP = 1, NP
*
*          If the current secondary is a photon (7)
           IF(KPART(IP) .EQ. 7) THEN
*           
*            Kinetic energy of the secondary
             SPAUSR(1) = Tki(IP)

*            Flag particle to be a true FN/PG
             LLOUSE = 1
*
*          If the current secondary is a neutron (8)
           ELSE IF(KPART(IP) .EQ. 8) THEN
*
*            Kinetic energy of the secondary
             SPAUSR(1) = Tki(IP)
*
*            Flag particle to be a true FN/PG
             LLOUSE = 1
*
           END IF
          END DO
         END IF
        END IF
      END IF    
*       
*------------------INTERACTIONS IN THE ELECTRONIC BOXES--------------------------
*      If an interaction happens in the electronic boxes (or the void inside them), 
*      then the particle is no longer a true FN/PG-particle (loss of coincidence)
*
      IF (MREG .GE. 57 .AND. MREG .LE. 200) THEN
*
*       Reset true FN/PG-flag to 0 (non-FN/PG)
        LLOUSE = 0
*
      END IF

*----------------------INTERACTIONS IN THE SCINTILLATORS------------------------------
      OPEN(UNIT=80, 
     &      FILE = 'scintillator_interactions.txt', STATUS='UNKNOWN')
*
*     If an interaction happens in the scintillator bars
      IF (MREG .GE. 1 .AND. MREG .LE. 48) THEN
*
*      If a true FN/PG does something it shouldn't do, it loses the status of a "true" FN/PG
*      This is meant to be rough check, not a full physics check.
       IF(LLOUSE .EQ. 1) THEN

*       If the interaction is not any of the "wanted" ICODEs, reset the "true" FN/PG flag
        IF(ICODE .NE. 219 .AND. ICODE .NE. 221 .AND.  
     &  ICODE .NE. 100 .AND. ICODE .NE. 300) THEN
          LLOUSE = 0
        END IF
        
*       If the ICODE is 300, things get more complicated. Extra checks are required
        IF(ICODE .EQ. 300) THEN
*
*         If there are fewer than or more than 2 secondaries, then it is not a wanted interaction
          IF(NP .NE. 2) THEN
            LLOUSE = 0

          ELSE
*           The only wanted interactions are JTRACK=8, KPART(1)=1, KPART(2)=8
*           Any other combination will have their "true" FN/PG-flag reset to 0
            IF(
     &      JTRACK .NE. 8 .OR. KPART(1) .NE. 1 .OR. KPART(2) .NE. 8
     &      ) THEN
              LLOUSE = 0
            END IF
          END IF
        END IF
       END IF
*--------------------------------OUTPUT------------------------------------------
*      Loop over all the secondaries created in the interaction.
       DO IP = 1, NP

*        Reassigning KPART(IP) to return something sensible (Carbon-12: -601200 -> -2 (Heavy ion))
         IF(KPART(IP) .LE. -300000) THEN

*         Write output file: 'FN_PG_detected.txt'
          WRITE(80,'(1I8,1X,6I3,1X,2F11.6,1X,3F10.5,1X,2I5,1X,4F11.6)')
     &     NCASE, ICODE, JTRACK, -2, LLOUSE, 
     &     ICHTAR, IBTAR, Tki(IP), ETRACK-AM(JTRACK),
     &     XSCO, YSCO, ZSCO, 
     &     MREG, LTRACK, ATRACK*1E6,
     &     SPAUSR(2), SPAUSR(3), SPAUSR(4)
*
         ELSE

*         Write output file: 'FN_PG_detected.txt' 
          WRITE(80,'(1I8,1X,6I3,1X,2F11.6,1X,3F10.5,1X,2I5,1X,4F11.6)')
     &     NCASE, ICODE, JTRACK, KPART(IP), LLOUSE,
     &     ICHTAR, IBTAR, Tki(IP), ETRACK-AM(JTRACK),
     &     XSCO, YSCO, ZSCO, 
     &     MREG, LTRACK, ATRACK*1E6,
     &     SPAUSR(2), SPAUSR(3), SPAUSR(4)
         END IF       

       END DO
*------------------------------END OF OUTPUT-----------------------------------------
*     If the particle interacts in the void (in case of air), then it is no longer a true FN/PG
      ELSE IF (MREG .GE. 50 .AND. MREG .LE. 55) THEN
       LLOUSE = 0
      END IF

* Np = total number of secondaries *
* Kpart (ip) = (Paprop) id of the ip_th secondary *
* Cxr (ip) = x-axis direction cosine of the ip_th secondary *
* Tki (ip) = laboratory kinetic energy of ip_th secondary (GeV)*
* Wei (ip) = statistical weight of the ip_th secondary *
* etc. (look up the full list in $FLUPRO/flukapro/(GENSTK) 

**************************** END ADDED BY SANDER IN USDRAW *************************

      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )
      END IF
* No output by default:
      RETURN
      CLOSE(80)
  
*=== End of subrutine Mgdraw ==========================================*    
      END
